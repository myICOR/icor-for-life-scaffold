#!/usr/bin/env python3
"""release/align.py: pin writes the lock, check finds every difference, rollout fixes them with a backup. Stdlib only."""
import hashlib, json, shutil, subprocess, sys, tempfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "release/align.py"
fails = cases = 0
sha = lambda b: hashlib.sha256(b).hexdigest()


def check(name, ok, info=None):
    global fails, cases
    cases += 1
    if not ok:
        fails += 1
        print(f"  FAIL {name}: {info}")


def run(t, *args):
    r = subprocess.run([sys.executable, "-B", str(TOOL), "--lock", str(t / "lock.json"), "--config", str(t / "vaults.json"), *args],
                       capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def build(folder, files):
    folder.mkdir(parents=True, exist_ok=True)
    for name, text in files.items():
        (folder / name).write_text(text)
    return folder


with tempfile.TemporaryDirectory() as td:
    t = Path(td)
    staging = t / "staging"
    v1, v2 = t / "Vault One", t / "Vault Two"
    # a lock of one plugin and the theme, and the builds it pins
    p1 = build(staging / "icor-for-life-demo", {"main.js": "v1", "manifest.json": json.dumps({"id": "icor-for-life-demo", "version": "1.0.0"})})
    th = build(staging / "icor-for-life-inkline", {"theme.css": "a{}", "manifest.json": json.dumps({"name": "ICOR for Life - INKLINE", "version": "1.0.0"})})
    lock = {"$comment": "test",
            "theme": {"name": "ICOR for Life - INKLINE", "version": "1.0.0", "source": {"local": str(th)},
                      "files": {f: sha((th / f).read_bytes()) for f in ("theme.css", "manifest.json")}},
            "plugins": [{"id": "icor-for-life-demo", "version": "1.0.0", "source": {"local": str(p1)},
                         "files": {f: sha((p1 / f).read_bytes()) for f in ("main.js", "manifest.json")}}]}
    (t / "lock.json").write_text(json.dumps(lock, indent=2) + "\n")
    (t / "vaults.json").write_text(json.dumps({"staging": str(staging), "vaults": [str(v1), str(v2)]}))
    for v in (v1, v2):
        shutil.copytree(p1, v / ".obsidian/plugins/icor-for-life-demo")
        shutil.copytree(th, v / ".obsidian/themes/ICOR for Life - INKLINE")
        (v / ".obsidian/plugins/icor-for-life-demo/data.json").write_text('{"secret": "keep"}')

    code, out = run(t, "check")
    check("aligned: check passes", code == 0 and "OK the lock, its builds and every vault agree" in out, out)

    # a new build: pin it
    new = build(t / "build", {"main.js": "v2", "manifest.json": json.dumps({"id": "icor-for-life-demo", "version": "1.1.0"}), "styles.css": "x{}"})
    code, out = run(t, "pin", str(new))
    pinned = json.loads((t / "lock.json").read_text())["plugins"][0]
    check("pin: OK and the version", code == 0 and pinned["version"] == "1.1.0", out)
    check("pin: every file by sha, styles.css added", pinned["files"] == {f: sha((new / f).read_bytes()) for f in ("main.js", "manifest.json", "styles.css")}, pinned)
    check("pin: copied into staging", (staging / "icor-for-life-demo/main.js").read_text() == "v2", out)

    code, out = run(t, "check")
    check("after pin: check fails and names both vaults", code == 1 and "Vault One: plugin icor-for-life-demo is not 1.1.0" in out and "Vault Two" in out, out)

    code, out = run(t, "rollout", "--no-reload")
    check("rollout: OK", code == 0 and out.count("UPDATED") == 2, out)
    check("rollout: the vault has the new build", (v1 / ".obsidian/plugins/icor-for-life-demo/main.js").read_text() == "v2", out)
    check("rollout: data.json untouched", (v1 / ".obsidian/plugins/icor-for-life-demo/data.json").read_text() == '{"secret": "keep"}', out)
    backups = list((v1 / ".icor-for-life/backups").glob("rollout-*/.obsidian/plugins/icor-for-life-demo/main.js"))
    check("rollout: the replaced file is backed up", len(backups) == 1 and backups[0].read_text() == "v1", backups)
    code, out = run(t, "check")
    check("after rollout: aligned again", code == 0, out)

    # the theme, a plugin the lock does not know, a build that drifted from the lock, a missing plugin
    nt = build(t / "theme-build", {"theme.css": "b{}", "manifest.json": json.dumps({"name": "ICOR for Life - INKLINE", "version": "1.1.0"})})
    code, out = run(t, "pin", str(nt))
    check("pin a theme", code == 0 and json.loads((t / "lock.json").read_text())["theme"]["version"] == "1.1.0", out)
    code, out = run(t, "pin", str(build(t / "stranger", {"main.js": "x", "manifest.json": json.dumps({"id": "someone-else", "version": "1"})})))
    check("pin refuses a plugin the lock does not have", code != 0 and "not in the lock" in out, out)
    (staging / "icor-for-life-demo/main.js").write_text("tampered")
    code, out = run(t, "rollout", "--no-reload")
    check("rollout refuses a build that is not the pinned one, and copies nothing",
          code != 0 and "nothing copied" in out and (v1 / ".obsidian/themes/ICOR for Life - INKLINE/theme.css").read_text() == "a{}", out)
    (staging / "icor-for-life-demo/main.js").write_text("v2")
    shutil.rmtree(v2 / ".obsidian/plugins/icor-for-life-demo")
    code, out = run(t, "rollout", "--no-reload")
    check("rollout: the theme reaches both vaults", (v2 / ".obsidian/themes/ICOR for Life - INKLINE/theme.css").read_text() == "b{}", out)
    check("rollout never installs a plugin, it says so", not (v2 / ".obsidian/plugins/icor-for-life-demo").exists() and "is not installed" in out, out)
    code, out = run(t, "check")
    check("check reports the plugin that is not installed", code == 1 and "Vault Two: plugin icor-for-life-demo is not installed" in out, out)

    (t / "vaults.json").unlink()
    code, out = run(t, "check")
    check("no config: check fails and says where the vaults go", code == 1 and "no vaults" in out, out)

print(f"FAIL {fails} of {cases} cases" if fails else f"OK {cases} cases held")
sys.exit(1 if fails else 0)
