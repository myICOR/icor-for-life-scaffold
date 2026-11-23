#!/usr/bin/env python3
"""test-migrate.py: migrate-to-3.py carries a 2.3 folder and an early 3.0 folder to the ICOR stage numbers.

Each case builds a small vault in a temporary folder, runs the script from this repository (the "3.0 download") dry
and live, and checks what moved, what was rewritten and what was left alone. Exit 0 when every case holds."""
import json, subprocess, sys, tempfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "_System/Tools/migrate-to-3.py"
fails, checks = [], 0


def check(name, ok, detail=""):
    global checks
    checks += 1
    print(("  ok   " if ok else "  FAIL ") + name + ("" if ok else f": {detail}"))
    if not ok:
        fails.append(name)


def write(root: Path, rel: str, text: str):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


def run(vault: Path, *args):
    return subprocess.run([sys.executable, str(SCRIPT), str(vault), *args], capture_output=True, text=True)


def vault_2x(root: Path, version: str, outer: bool, team: bool):
    """The old layout: 00 Daily Scratchpad, 02 Planner, 04 Inner World, 05 Assets (and 06 Outer World, 07 Databases on
    an early 3.0; 03 WiP and 06 AI Team on a 2.3)."""
    write(root, ".icor-for-life/VERSION", version + "\n")
    write(root, "00 Daily Scratchpad/2026/11/2026-11-02.md", "a day\n")
    write(root, "02 Planner/Manual/Call Ana.md", "---\ntype: planner-item\n---\n")
    write(root, "04 Inner World/Notes/Trip.md", "![[05 Assets/Images/map.png]] and [[04 Inner World/Notes/Other|other]]\n"
                                                 "In 04 Inner World-ish words nothing changes: 04 Inner Worlds.\n")
    write(root, "04 Inner World/Notes/Trip.base", 'filters:\n  and:\n    - file.inFolder("04 Inner World/Notes")\n')
    write(root, "05 Assets/Images/map.png", "png")
    write(root, ".obsidian/daily-notes.json", json.dumps({"folder": "00 Daily Scratchpad", "format": "YYYY/MM/YYYY-MM-DD"}))
    write(root, ".obsidian/app.json", json.dumps({"attachmentFolderPath": "05 Assets/Images"}))
    write(root, ".obsidian/plugins/icor-for-life-planner/data.json", json.dumps({"folder": "02 Planner"}))
    write(root, ".obsidian/plugins/icor-for-life-planner/main.js", 'const DEFAULT = "02 Planner";')
    if outer:
        write(root, "06 Outer World/Book.md", "---\ntype: source\n---\n")
        write(root, "07 Databases/Objects.base", "views: []\n")
    if team:
        write(root, "03 WiP/draft.md", "work in 04 Inner World\n")
        write(root, "06 AI Team/Agents/Penn/notes.md", "files into 04 Inner World/Journal\n")
        write(root, ".mypka/state.json", json.dumps({"inbox": "00 Daily Scratchpad"}))


def cases(tmp: Path):
    print("a 2.3 folder with a myPKA team")
    v = tmp / "two"
    vault_2x(v, "2.3.0", outer=False, team=True)
    r = run(v)
    check("the dry run names each folder it would rename",
          all(f"folder {a} → {b}" in r.stdout for a, b in (("00 Daily Scratchpad", "00 Daily Notes"), ("02 Planner", "06 Planner"),
                                                         ("04 Inner World", "02 Inner World"), ("05 Assets", "04 Assets"))),
          r.stdout + r.stderr)
    check("the dry run changes nothing", (v / "04 Inner World").is_dir() and not (v / "02 Inner World").exists(), r.stdout)
    r = run(v, "--live")
    check("the live run ends OK", r.returncode == 0 and "OK done" in r.stdout, r.stdout + r.stderr)
    for name in ("00 Daily Notes", "02 Inner World", "04 Assets", "06 Planner"):
        check(f"{name} exists", (v / name).is_dir())
    for name in ("00 Daily Scratchpad", "02 Planner", "04 Inner World", "05 Assets"):
        check(f"{name} is gone", not (v / name).exists())
    trip = (v / "02 Inner World/Notes/Trip.md").read_text()
    check("an embed path and a link path follow", "![[04 Assets/Images/map.png]]" in trip and "[[02 Inner World/Notes/Other|other]]" in trip, trip)
    check("a name that only starts like a folder is left", "04 Inner World-ish" in trip and "04 Inner Worlds" in trip, trip)
    check("a base's folder filter follows", 'file.inFolder("02 Inner World/Notes")' in (v / "02 Inner World/Notes/Trip.base").read_text())
    check("Daily notes opens 00 Daily Notes", json.loads((v / ".obsidian/daily-notes.json").read_text())["folder"] == "00 Daily Notes")
    check("attachments go to 04 Assets/Images", json.loads((v / ".obsidian/app.json").read_text())["attachmentFolderPath"] == "04 Assets/Images")
    check("a plugin's saved settings follow", json.loads((v / ".obsidian/plugins/icor-for-life-planner/data.json").read_text())["folder"] == "06 Planner")
    check("a plugin's code is never rewritten", '"02 Planner"' in (v / ".obsidian/plugins/icor-for-life-planner/main.js").read_text())
    check("the myPKA team's files are left as they are",
          "04 Inner World/Journal" in (v / "06 AI Team/Agents/Penn/notes.md").read_text()
          and "00 Daily Scratchpad" in (v / ".mypka/state.json").read_text())
    check("06 AI Team stays beside the new 06 Planner", (v / "06 AI Team").is_dir() and (v / "06 Planner").is_dir())
    r = run(v, "--live")
    check("a second run finds nothing to do", "already" in r.stdout + r.stderr and not (v / "04 Inner World").exists(), r.stdout + r.stderr)

    print("an early 3.0 folder")
    v = tmp / "early"
    vault_2x(v, "3.0.0", outer=True, team=False)
    r = run(v, "--live")
    check("an early 3.0 folder is not turned away", r.returncode == 0 and "already" not in r.stdout, r.stdout + r.stderr)
    for was, now in (("06 Outer World", "03 Outer World"), ("07 Databases", "05 Databases")):
        check(f"{was} → {now}", (v / now).is_dir() and not (v / was).exists())
    r = run(v)
    check("a folder already on the stage numbers is left alone", "already 3.0.0" in r.stdout + r.stderr, r.stdout + r.stderr)

    print("both names exist")
    v = tmp / "both"
    vault_2x(v, "2.3.0", outer=False, team=False)
    write(v, "02 Inner World/Notes/New.md", "new\n")
    r = run(v, "--live")
    check("the old folder is left and the person is told",
          (v / "04 Inner World").is_dir() and "Both 04 Inner World and 02 Inner World exist" in r.stdout, r.stdout + r.stderr)
    check("the paths of a folder that did not move are not rewritten", "[[04 Inner World/Notes/Other" in (v / "04 Inner World/Notes/Trip.md").read_text())


def main():
    with tempfile.TemporaryDirectory(prefix="test-migrate.") as tmp:
        cases(Path(tmp))
    if fails:
        print("FAIL %d of %d cases" % (len(fails), checks))
        return 1
    print("OK %d cases held" % checks)
    return 0


if __name__ == "__main__":
    sys.exit(main())
