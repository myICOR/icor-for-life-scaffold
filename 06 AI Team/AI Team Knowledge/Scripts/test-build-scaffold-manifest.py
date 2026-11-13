#!/usr/bin/env python3
"""test-build-scaffold-manifest.py: the fixture suite behind the manifest's
`previous_removed` map (build-scaffold-manifest.py).

Builds a throwaway git repository in a temp folder with four tagged
versions, runs the real builder in it, and asserts what `previous_removed`
holds: every older state of a removed or renamed-away path that its
`history` entry does not already name, nothing for a path that never
changed, nothing for a path that moved to myPKA, nothing for a path the
release still ships (that is `previous`), and a --check that goes red when
the map is dropped from the manifest on disk. Idea: Brian Carroll
(@brijcarroll), who found that an untouched copy of an older version was
reported as the member's own file.

Run it with --break-me to prove the suite itself can go red: it asserts the
opposite of one held rule and the run must end in FAIL.

Usage:  test-build-scaffold-manifest.py [--break-me]
Exit 0 = every case held. Exit 1 = a case did not.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# No bytecode into the folder this suite lives in (see test-life-snapshot.py).
sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
BUILDER = HERE / "build-scaffold-manifest.py"
SCRIPTS = "06 AI Team/AI Team Knowledge/Scripts"
PY = sys.executable
BREAK = "--break-me" in sys.argv[1:]

checks = 0
fails = []


def check(label, ok, detail=""):
    global checks
    checks += 1
    print(("  ok    " if ok else "  FAIL  ") + label)
    if not ok:
        fails.append(label + (": " + detail.strip()[-300:] if detail else ""))


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def write(root, rel, text):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def git(root, *args):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    return subprocess.run(["git", "-C", str(root), "-c", "user.name=fixture", "-c", "user.email=fixture@localhost",
                           "-c", "commit.gpgsign=false", "-c", "tag.gpgsign=false", "-c", "init.defaultBranch=main",
                           *args], capture_output=True, text=True, check=True, env=env)


def cut(root, version, changelog):
    """Commit the tree as `version`, with a changelog section per version."""
    write(root, ".icor-for-life/VERSION", version + "\n")
    write(root, ".icor-for-life/CHANGELOG.md", "# Changelog\n\n" + "".join(
        "## %s\n\n%s\n" % (v, body) for v, body in changelog))
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "release " + version)


def build(root, *args):
    return subprocess.run([PY, str(root / SCRIPTS / "build-scaffold-manifest.py"), *args],
                          cwd=str(root), capture_output=True, text=True)


if not BUILDER.is_file():
    print("FAIL build-scaffold-manifest.py is not beside this suite", file=sys.stderr)
    sys.exit(1)

with tempfile.TemporaryDirectory(prefix="icor-manifest-") as td:
    R = Path(td) / "scaffold"
    R.mkdir()
    git(R, "init", "-q")
    # The smallest tree the builder reads: its own copy, the REQUIRED list it
    # lifts out of validate-scaffold.py, a RESIDUE_PATHS array naming a
    # tracked file, and the two Obsidian files it reads.
    (R / SCRIPTS).mkdir(parents=True)
    shutil.copy2(BUILDER, R / SCRIPTS / "build-scaffold-manifest.py")
    write(R, SCRIPTS + "/validate-scaffold.py", 'REQUIRED = ["04 Inner World"]\n')
    write(R, SCRIPTS + "/build-release-zip.sh",
          'declare -a RESIDUE_PATHS=(\n  "06 AI Team/AI Team Knowledge/Scripts/build-release-zip.sh"\n)\n')
    write(R, ".obsidian/community-plugins.json", "[]\n")
    write(R, ".obsidian/appearance.json", "{}\n")
    write(R, "04 Inner World/README.md", "# Inner World\n")

    X = "04 Inner World/x.md"        # three states, then removed
    Y = "04 Inner World/y.md"        # one state, then removed
    M = "06 AI Team/m.md"            # two states, then moved to myPKA
    R_OLD = "04 Inner World/old.md"  # two states, then renamed
    R_NEW = "04 Inner World/new.md"
    K = "04 Inner World/kept.md"     # two states, still shipped

    log = []
    write(R, X, "x one\n"); write(R, Y, "y only\n"); write(R, M, "m one\n")
    write(R, R_OLD, "old one\n"); write(R, K, "kept one\n")
    log.insert(0, ("1.0.0", "- Added: the fixture.\n")); cut(R, "1.0.0", log); git(R, "tag", "1.0.0")

    write(R, X, "x two\n"); write(R, M, "m two\n"); write(R, R_OLD, "old two\n"); write(R, K, "kept two\n")
    log.insert(0, ("1.1.0", "- Changed: x, m, old and kept.\n")); cut(R, "1.1.0", log); git(R, "tag", "1.1.0")

    write(R, X, "x three\n")
    log.insert(0, ("1.2.0", "- Changed: x.\n")); cut(R, "1.2.0", log); git(R, "tag", "1.2.0")

    # 1.3.0 is the untagged HEAD, the state a manifest is built in.
    (R / X).unlink(); (R / Y).unlink(); (R / M).unlink()
    (R / R_OLD).rename(R / R_NEW)
    log.insert(0, ("1.3.0", "- Removed: `%s`, the x note.\n- Removed: `%s`, the y note.\n" % (X, Y)))
    cut(R, "1.3.0", log)

    # myPKA ships m.md, so its removal is a move.
    UP = Path(td) / "mypka"
    write(UP, ".mypka/manifest.json", json.dumps({"files": {M: sha("m two\n")}}))

    print("build")
    r = build(R, "--upstream", str(UP))
    check("the builder writes the manifest", r.returncode == 0, r.stderr + r.stdout)
    man = json.loads((R / ".icor-for-life/manifest.json").read_text(encoding="utf-8")) if r.returncode == 0 else {}
    pr = man.get("previous_removed")
    check("the manifest carries previous_removed as a map", isinstance(pr, dict), repr(pr))
    pr = pr if isinstance(pr, dict) else {}
    removed = {e["path"]: e for h in man.get("history") or [] for e in h.get("removed") or []}

    print("previous_removed")
    check("history names only the last shipped state of x", removed.get(X, {}).get("sha256") == sha("x three\n"),
          repr(removed.get(X)))
    check("x lists its two older states", pr.get(X) == sorted([sha("x one\n"), sha("x two\n")]), repr(pr.get(X)))
    check("x does not repeat the state history already names", sha("x three\n") not in (pr.get(X) or []))
    check("y never changed, so it is not listed", Y not in pr, repr(pr.get(Y)))
    check("m moved to myPKA and is not listed", removed.get(M, {}).get("moved_to") == "mypka" and M not in pr,
          repr(removed.get(M)) + " " + repr(pr.get(M)))
    check("a path renamed away lists its older state", pr.get(R_OLD) == [sha("old one\n")], repr(pr.get(R_OLD)))
    check("the rename's new path is not listed", R_NEW not in pr)
    check("a path still shipped is not listed (previous holds it)",
          K not in pr and (man.get("previous") or {}).get(K) == [sha("kept one\n")],
          repr(pr.get(K)) + " " + repr((man.get("previous") or {}).get(K)))
    check("nothing else is listed", sorted(pr) == sorted([X, R_OLD]), repr(sorted(pr)))

    print("seed")
    # 2.3.0: the plugins stopped shipping and the download enables none. An
    # untouched copy of an older enabled list must not be overwritten by the
    # updater with `[]`, or every plugin a member installed switches off.
    check("the enabled-plugin list is a seed, the member's after the first install",
          ".obsidian/community-plugins.json" in (man.get("seed") or []), repr(man.get("seed")))

    print("check")
    # The manifest was untracked on the first build; once tracked it lists
    # itself, so build once more, as the release order does (build, amend).
    git(R, "add", "-A"); git(R, "commit", "-q", "--amend", "--no-edit")
    build(R, "--upstream", str(UP))
    git(R, "add", "-A"); git(R, "commit", "-q", "--amend", "--no-edit")
    r2 = build(R, "--check", "--upstream", str(UP))
    check("--check is green on the manifest just built", r2.returncode == 0, r2.stderr)
    first = (R / ".icor-for-life/manifest.json").read_bytes()
    r3 = build(R, "--upstream", str(UP))
    strip = lambda b: {k: v for k, v in json.loads(b).items() if k not in ("built", "commit")}
    check("a rebuild gives the same manifest (bar built and commit)",
          r3.returncode == 0 and strip(first) == strip((R / ".icor-for-life/manifest.json").read_bytes()))
    stale = json.loads((R / ".icor-for-life/manifest.json").read_text(encoding="utf-8"))
    stale.pop("previous_removed", None)
    write(R, ".icor-for-life/manifest.json", json.dumps(stale, indent=2) + "\n")
    r4 = build(R, "--check", "--upstream", str(UP))
    check("--check is red when the map is missing from the manifest on disk",
          r4.returncode == 1 and "stale in: previous_removed;" in r4.stderr, r4.stderr)

    if BREAK:
        check("DELIBERATE: y must be listed (it must not be)", Y in pr, "the suite is proving it can go red")

print()
if fails:
    print("FAIL %d of %d cases" % (len(fails), checks), file=sys.stderr)
    for f in fails:
        print("  " + f, file=sys.stderr)
    sys.exit(1)
print("OK %d cases held" % checks)
sys.exit(0)
