#!/usr/bin/env python3
"""align.py: keep the lock, its builds and the maintainer's vaults on the same plugins and theme, on demand.

    python3 release/align.py pin <build folder>    a new plugin or theme build into the lock
    python3 release/align.py rollout               every vault to the lock, with a backup first
    python3 release/align.py check                 is everything the same? exit 1 if anything differs

Tom, 2026-11-28: the hourly launchd job (com.myicor.vault-sync) is gone. It read a stale lock and put old plugins back
into the Demo vault four times in one day. Nothing runs on a schedule now: a change is pinned, committed and rolled
out in the same piece of work, and `check` proves the three places agree.

THE ORDER, every time (the scaffold first, then both vaults):
  1. build the plugin or theme in its repository, merge it;
  2. `pin <build folder>`: copies the build's files into the staging folder and writes its version and the sha256 of
     every file into release/plugins.lock.json;
  3. commit and push the lock;
  4. `rollout`: copies every file that differs from the lock into each vault, after backing up the file it replaces
     to <vault>/.icor-for-life/backups/rollout-<time>/, then reloads the changed plugins in a vault Obsidian has open;
  5. `check`: the lock is committed and pushed, every build matches the lock, every vault matches the lock.

WHERE THE VAULTS ARE is personal, so it is not in the repository: release/vaults.local.json (ignored by git):
    {"staging": "/path/to/plugins-staging", "vaults": ["/path/to/vault one", "/path/to/vault two"]}
`--vault <path>` (repeatable) and `--staging <path>` replace it for one run.

What it never does: install a plugin a vault does not have (it reports it), touch data.json or a note, enable or
disable anything, push, tag or release. ICOR Terminal is not reloaded, because a reload ends every terminal session
open in it: its new build takes effect at the next Obsidian start (--reload-terminal to reload it anyway).
"""
import argparse, hashlib, json, shutil, subprocess, sys, time
from pathlib import Path

sys.dont_write_bytecode = True
REPO = Path(__file__).resolve().parent.parent
LOCK = REPO / "release" / "plugins.lock.json"
CONFIG = REPO / "release" / "vaults.local.json"
THEME_FOLDER = "icor-for-life-inkline"          # the theme's folder in staging
PLUGIN_FILES = ["main.js", "manifest.json", "styles.css"]
THEME_FILES = ["theme.css", "manifest.json"]
NO_RELOAD = {"icor-for-life-terminal"}          # a reload ends the open terminal sessions


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None


def load_lock(path):
    return json.loads(path.read_text(encoding="utf-8"))


def save_lock(path, lock):
    path.write_text(json.dumps(lock, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def entries(lock):
    """(kind, name, entry, path inside a vault) for every plugin and the theme."""
    out = [("plugin", p["id"], p, f".obsidian/plugins/{p['id']}") for p in lock["plugins"]]
    t = lock["theme"]
    out.append(("theme", t["name"], t, f".obsidian/themes/{t['name']}"))
    return out


def settings(args):
    conf = {}
    if args.config.is_file():
        conf = json.loads(args.config.read_text(encoding="utf-8"))
    vaults = [Path(v).expanduser() for v in (args.vault or conf.get("vaults", []))]
    staging = args.staging or conf.get("staging")
    return vaults, (Path(staging).expanduser() if staging else None)


# ------------------------------------------------------------------ pin --
def pin(args):
    build = Path(args.build).expanduser().resolve()
    if not (build / "manifest.json").is_file():
        raise SystemExit(f"FAIL {build} has no manifest.json")
    manifest = json.loads((build / "manifest.json").read_text(encoding="utf-8"))
    _, staging = settings(args)
    if staging is None:
        raise SystemExit(f"FAIL no staging folder: set \"staging\" in {args.config.name} or pass --staging")
    lock = load_lock(args.lock)
    if (build / "theme.css").is_file():
        entry, target, names = lock["theme"], staging / THEME_FOLDER, THEME_FILES
        if manifest.get("name") != entry["name"]:
            raise SystemExit(f"FAIL {build} is the theme {manifest.get('name')!r}, the lock pins {entry['name']!r}")
    else:
        pid = manifest.get("id")
        entry = next((p for p in lock["plugins"] if p["id"] == pid), None)
        if entry is None:
            raise SystemExit(f"FAIL {pid!r} is not in the lock; a new plugin goes into the lock by hand, deliberately")
        target = staging / pid
        names = list(dict.fromkeys(list(entry["files"]) + [f for f in PLUGIN_FILES if (build / f).is_file()]))
    missing = [f for f in names if not (build / f).is_file()]
    if missing:
        raise SystemExit(f"FAIL {build} lacks {', '.join(missing)}")
    target.mkdir(parents=True, exist_ok=True)
    for f in names:
        shutil.copyfile(build / f, target / f)
    was = entry["version"]
    entry["version"] = manifest["version"]
    entry["source"] = {"local": str(target)}
    entry["files"] = {f: sha(target / f) for f in names}
    save_lock(args.lock, lock)
    name = entry.get("id", entry.get("name"))
    print(f"OK pinned {name} {was} -> {entry['version']} ({', '.join(names)}); commit and push the lock, then rollout")
    return 0


# -------------------------------------------------------------- compare --
def source_problems(lock):
    """Every lock entry whose local source does not hold exactly the pinned files."""
    out = []
    for kind, name, e, _ in entries(lock):
        src = e.get("source", {})
        if "local" not in src:
            continue  # a GitHub release: build-zip.py downloads and checks it
        bad = [f for f, h in e["files"].items() if sha(Path(src["local"]) / f) != h]
        if bad:
            out.append(f"{kind} {name} {e['version']}: the build in {src['local']} is not the pinned one ({', '.join(bad)})")
    return out


def vault_diffs(lock, vault):
    """Every installed entry that differs from the lock, as (name, kind, entry, folder, files); and what is not installed."""
    diffs, missing = [], []
    for kind, name, e, rel in entries(lock):
        target = vault / rel
        if not target.is_dir():
            missing.append(f"{kind} {name}")
            continue
        stale = [f for f, h in e["files"].items() if sha(target / f) != h]
        if stale:
            diffs.append((name, kind, e, target, stale))
    return diffs, missing


def git_state(lock_path):
    """Problems with the lock in git: changes not committed, or commits not pushed."""
    def git(*a):
        return subprocess.run(["git", "-C", str(lock_path.parent), *a], capture_output=True, text=True)
    if git("rev-parse", "--is-inside-work-tree").returncode:
        return []
    out = []
    if git("status", "--porcelain", "--", str(lock_path)).stdout.strip():
        out.append("the lock has changes that are not committed")
    ahead = git("rev-list", "--count", "@{upstream}..HEAD")
    if ahead.returncode == 0 and ahead.stdout.strip() not in ("", "0"):
        out.append(f"{ahead.stdout.strip()} commit(s) not pushed")
    return out


# ---------------------------------------------------------------- check --
def check(args):
    lock = load_lock(args.lock)
    vaults, _ = settings(args)
    problems = [f"scaffold: {p}" for p in git_state(args.lock)] + [f"source: {p}" for p in source_problems(lock)]
    if not vaults:
        problems.append(f"no vaults: list them in {args.config.name} or pass --vault")
    for v in vaults:
        if not (v / ".obsidian").is_dir():
            problems.append(f"{v.name}: not found at {v}")
            continue
        diffs, missing = vault_diffs(lock, v)
        for name, kind, e, _, stale in diffs:
            problems.append(f"{v.name}: {kind} {name} is not {e['version']} ({', '.join(stale)})")
        for m in missing:
            problems.append(f"{v.name}: {m} is not installed")
        if not diffs and not missing:
            print(f"OK {v.name}: all {len(entries(lock))} match the lock")
    for p in problems:
        print(f"DIFF {p}")
    if problems:
        print(f"FAIL {len(problems)} difference(s): pin, commit and push, then rollout")
        return 1
    print("OK the lock, its builds and every vault agree")
    return 0


# -------------------------------------------------------------- rollout --
def open_vaults():
    try:
        d = json.loads((Path.home() / "Library/Application Support/obsidian/obsidian.json").read_text())
        return {Path(v["path"]).resolve() for v in d.get("vaults", {}).values() if v.get("open")}
    except (OSError, ValueError):
        return set()


def obsidian(vault, *a):
    try:
        r = subprocess.run(["obsidian", f"vault={vault.name}", *a], capture_output=True, text=True, timeout=60)
        return r.returncode == 0, (r.stdout or r.stderr).strip()
    except (OSError, subprocess.TimeoutExpired) as e:
        return False, str(e)


def rollout(args):
    lock = load_lock(args.lock)
    vaults, _ = settings(args)
    if not vaults:
        raise SystemExit(f"FAIL no vaults: list them in {args.config.name} or pass --vault")
    bad = source_problems(lock)
    if bad:
        for b in bad:
            print(f"FAIL source: {b}")
        raise SystemExit("FAIL nothing copied: the builds do not match the lock (pin them again)")
    stamp = time.strftime("%Y%m%d-%H%M%S")
    opened = set() if args.no_reload else open_vaults()
    changed = 0
    for v in vaults:
        if not (v / ".obsidian").is_dir():
            print(f"SKIP {v}: not found")
            continue
        diffs, missing = vault_diffs(lock, v)
        backup = v / ".icor-for-life" / "backups" / f"rollout-{stamp}"
        reload_plugins, theme_changed = [], False
        for name, kind, e, target, stale in diffs:
            src = Path(e["source"]["local"])
            for f in stale:
                if (target / f).is_file():
                    keep = backup / target.relative_to(v) / f
                    keep.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(target / f, keep)
                tmp = target / f".align-{f}"
                shutil.copyfile(src / f, tmp)
                tmp.replace(target / f)  # one step: Obsidian never reads half a file
            print(f"UPDATED {v.name}: {kind} {name} {e['version']} ({', '.join(stale)})")
            changed += 1
            if kind == "plugin":
                reload_plugins.append(name)
            else:
                theme_changed = True
        for m in missing:
            print(f"NOTE {v.name}: {m} is not installed; install it in Obsidian if this vault should have it")
        if diffs:
            print(f"     backup of what was replaced: {backup}")
        if v.resolve() in opened:
            for pid in reload_plugins:
                if pid in NO_RELOAD and not args.reload_terminal:
                    print(f"     {pid}: not reloaded (that would end open terminal sessions); it loads at the next Obsidian start")
                    continue
                ok, msg = obsidian(v, "plugin:reload", f"id={pid}")
                print(f"     reloaded {pid}" if ok else f"     RELOAD FAILED {pid}: {msg[:200]}")
            if theme_changed:
                code = ("(()=>{const t=app.customCss.theme;if(!t)return 'no theme';app.customCss.setTheme('');"
                        "setTimeout(()=>app.customCss.setTheme(t),300);return t})()")
                ok, msg = obsidian(v, "eval", f"code={code}")
                print("     theme reloaded" if ok else f"     THEME RELOAD FAILED: {msg[:200]}")
    if changed == 0:
        print("OK every vault already matches the lock")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--lock", type=Path, default=LOCK, help=argparse.SUPPRESS)
    ap.add_argument("--config", type=Path, default=CONFIG, help=argparse.SUPPRESS)
    ap.add_argument("--vault", action="append", help="a vault to align (repeatable); replaces the config's list")
    ap.add_argument("--staging", help="the staging folder; replaces the config's")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("pin", help="a new plugin or theme build into the lock")
    p.add_argument("build")
    sub.add_parser("check", help="exit 1 if the lock, its builds or a vault differ")
    r = sub.add_parser("rollout", help="every vault to the lock, with a backup")
    r.add_argument("--no-reload", action="store_true", help="do not reload anything in Obsidian")
    r.add_argument("--reload-terminal", action="store_true", help="reload ICOR Terminal too (ends its open sessions)")
    args = ap.parse_args(argv)
    return {"pin": pin, "check": check, "rollout": rollout}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
