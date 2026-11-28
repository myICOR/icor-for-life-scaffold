#!/usr/bin/env python3
"""ai-log.py: the first entry makes the day's file, later ones append, earlier entries stay byte for byte."""
import shutil, subprocess, sys, tempfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "_System/Tools/ai-log.py"
fails = cases = 0


def check(name, ok, info=None):
    global fails, cases
    cases += 1
    if not ok:
        fails += 1
        print(f"  FAIL {name}: {info}")


def run(root, *args):
    return subprocess.run([sys.executable, "-B", str(TOOL), "--root", str(root), *args], capture_output=True, text=True)


with tempfile.TemporaryDirectory() as td:
    v = Path(td) / "vault"
    (v / "_System").mkdir(parents=True)
    shutil.copy2(ROOT / "_System/schema.json", v / "_System/schema.json")
    day = v / "09 AI/Log/2026/11/2026-11-28.md"
    r = run(v, "--who", "Claude", "--where", "08 Workbench/2026-11-28 Plan", "--at", "2026-11-28T09:05", "Drafted plan.md")
    check("first entry: OK", r.returncode == 0 and r.stdout.startswith("OK 09 AI/Log/2026/11/2026-11-28.md"), r.stdout + r.stderr)
    first = day.read_text(encoding="utf-8")
    check("first entry: typed log with its date", first.startswith("---\ntype: log\ndate: 2026-11-28\ncreated: 2026-11-28\n---\n"), first)
    check("first entry: heading and line", "## 09:05 · Claude · 08 Workbench/2026-11-28 Plan\n- Drafted plan.md\n" in first, first)
    r = run(v, "--who", "Codex", "--at", "2026-11-28T17:30", "Filed a note", "Moved the folder to Done")
    after = day.read_text(encoding="utf-8")
    check("second entry: earlier text kept byte for byte", after.startswith(first), after)
    check("second entry: appended after a blank line", after.endswith("\n\n## 17:30 · Codex\n- Filed a note\n- Moved the folder to Done\n"), after)
    r = run(v, "--who", "Claude", "--at", "2026-12-01T08:00", "Next month")
    check("a new day gets its own file in its month", (v / "09 AI/Log/2026/12/2026-12-01.md").is_file(), r.stdout + r.stderr)
    r = run(v, "--who", "Claude", "   ")
    check("nothing to log: refused", r.returncode != 0 and "FAIL" in r.stdout + r.stderr, r.stdout + r.stderr)
    r = run(Path(td), "--who", "Claude", "x")
    check("not an ICOR for Life folder: refused", r.returncode != 0 and "FAIL" in r.stdout + r.stderr, r.stdout + r.stderr)

print(f"{'FAIL ' + str(fails) + ' of' if fails else 'OK'} {cases} cases {'' if fails else 'held'}".strip())
sys.exit(1 if fails else 0)
