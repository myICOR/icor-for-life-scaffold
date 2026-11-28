#!/usr/bin/env python3
"""A new journal entry (new-journal-entry.py and the template): the body starts right under the properties, the person's
words go under Original Text verbatim, and what an AI adds goes under AI Expansion (Tom, 2026-11-28). Stdlib only."""
import json, re, shutil, subprocess, sys, tempfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
fails = cases = 0


def check(name, ok, info=None):
    global fails, cases
    cases += 1
    if not ok:
        fails += 1
        print(f"  FAIL {name}: {info}")


with tempfile.TemporaryDirectory() as td:
    v = Path(td)
    (v / "_System").mkdir()
    shutil.copy2(ROOT / "_System/schema.json", v / "_System/schema.json")
    (v / "03 Journal").mkdir()
    words = "  A walk, indented on purpose.\n\nTwo paragraphs."
    r = subprocess.run([sys.executable, "-B", str(ROOT / "_System/Tools/new-journal-entry.py"), "--root", str(v), "--date", "2026-11-28",
                        "--slug", "a-walk", "--journal-type", "thought", "--original", words], capture_output=True, text=True)
    check("the tool says OK", r.returncode == 0 and r.stdout.startswith("OK"), r.stdout + r.stderr)
    text = (v / "03 Journal/2026/11/2026-11-28_a-walk.md").read_text(encoding="utf-8")
    body = text.split("\n---\n", 1)[1]
    check("the body starts right under the properties", body.startswith("## Original Text\n"), body[:40])
    check("the words, verbatim", f"## Original Text\n\n{words}\n" in body, body)
    check("the AI's section is AI Expansion", re.search(r"^## AI Expansion$", body, re.M) and not re.search(r"^## Expansion$", body, re.M), body)

tpl = (ROOT / "_System/Templates/journal.md").read_text(encoding="utf-8")
check("the template starts its body right under the properties", tpl.split("\n---\n", 1)[1].startswith("## Original Text\n"), tpl)
check("the template's AI section is AI Expansion", "\n## AI Expansion\n" in tpl and "\n## Expansion\n" not in tpl, tpl)
journal = json.loads((ROOT / "_System/schema.json").read_text(encoding="utf-8"))["types"]["journal"]
check("the schema names the sections", journal["sections"] == ["## Original Text", "## AI Expansion"], journal["sections"])
check("pinned is an optional journal field", "pinned" in journal["fields"] and "pinned" not in journal["required"], journal)

print(f"FAIL {fails} of {cases} cases" if fails else f"OK {cases} cases held")
sys.exit(1 if fails else 0)
