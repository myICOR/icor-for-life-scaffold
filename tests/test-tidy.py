#!/usr/bin/env python3
"""test-tidy.py: tidy-markdown.py. The top of a note (no blank first line, no title heading Obsidian already shows),
hard-wrapped Markdown joined into one line per paragraph, the check, the backup and the restore. Exit 0 when every
case holds."""
import importlib.util, subprocess, sys, tempfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "_System/Tools/tidy-markdown.py"
spec = importlib.util.spec_from_file_location("tidy", SCRIPT)
T = importlib.util.module_from_spec(spec); spec.loader.exec_module(T)
fails, checks = [], 0


def check(name, ok, detail=""):
    global checks
    checks += 1
    print(("  ok   " if ok else "  FAIL ") + name + ("" if ok else f": {detail!r}"))
    if not ok:
        fails.append(name)


print("tops")
fm = "---\ntype: food\ntags: []\n---\n"
t, c = T.tidy_top(fm + "\n# Apfelschorle\n\n## Notes\n", "Apfelschorle")
check("the blank line and the title heading go", t == fm + "## Notes\n" and c == ["blank line", "title heading"], t)
t, c = T.tidy_top(fm + "\n# merci-schokolade\nSweet.\n", "Merci Schokolade")
check("the title matches ignoring case, hyphens and spaces", t == fm + "Sweet.\n", t)
t, c = T.tidy_top(fm + "\n# Lunch: Alex\n", "Lunch Alex")
check("punctuation the file name could not hold still matches", t == fm, t)
t, c = T.tidy_top(fm + "# Something else\n\ntext\n", "Apfelschorle")
check("a heading that is not the file name stays", t == fm + "# Something else\n\ntext\n" and c == [], t)
t, c = T.tidy_top(fm + "\n## Original Text\n\nwords\n", "2026-11-02_walk")
check("a journal entry loses only the blank line", t == fm + "## Original Text\n\nwords\n" and c == ["blank line"], t)
t, c = T.tidy_top("---\ntype: person\n---\n\n# {{title}}\n\n", "person")
check("a template's {{title}} heading goes", t == "---\ntype: person\n---\n", t)
t, c = T.tidy_top("# Plain\n\ntext\n", "Plain")
check("a note without properties loses its title heading", t == "text\n" and c == ["title heading"], t)
t, c = T.tidy_top("\ntext\n", "x")
check("a note without properties keeps its leading blank line (there is no top to tidy)", t == "\ntext\n" and c == [], t)
t, c = T.tidy_top(fm + "text\n\n# Apfelschorle\n", "Apfelschorle")
check("only a FIRST heading counts", c == [], t)

print("unwrap")
src = ("---\ntitle: a\nlong: b\n---\nThis is a paragraph that was\nwrapped at a narrow width.\n\n"
       "- a list item that runs\n  on to a second line\n- the next item\n\n| a | b |\n| --- | --- |\n\n"
       "```\ncode stays\nas it is\n```\n\n> [!note] A callout\n> stays line by line\n\n![[a.png]]\n![[b.png]]\n\n"
       "Two spaces mean a break  \nso this stays.\n# Heading\nText under it.\n")
out, n = T.unwrap(src)
check("a paragraph becomes one line", "This is a paragraph that was wrapped at a narrow width.\n" in out, out)
check("a list item's indented line joins the item", "- a list item that runs on to a second line\n- the next item" in out, out)
check("tables, code, callouts and embeds stay", "| a | b |\n| --- | --- |" in out and "code stays\nas it is" in out
      and "> [!note] A callout\n> stays line by line" in out and "![[a.png]]\n![[b.png]]" in out, out)
check("front matter stays", out.startswith("---\ntitle: a\nlong: b\n---\n"), out)
check("a deliberate break stays", "break  \nso this stays." in out, out)
check("a heading is never joined", "\n# Heading\nText under it.\n" in out, out)
check("it counts what it joined", n == 2, n)
again, n2 = T.unwrap(out)
check("a second run joins nothing", again == out and n2 == 0, n2)

print("the tool")
with tempfile.TemporaryDirectory(prefix="test-tidy.") as tmp:
    v = Path(tmp)
    (v / "Food").mkdir()
    (v / "Food/Apfelschorle.md").write_text(fm + "\n# Apfelschorle\n\n## Notes\n", encoding="utf-8")
    (v / "Food/Keep.md").write_text(fm + "## Notes\n", encoding="utf-8")
    (v / ".obsidian").mkdir()
    (v / ".obsidian/x.md").write_text("---\na: 1\n---\n\n# x\n", encoding="utf-8")
    r = subprocess.run([sys.executable, str(SCRIPT), "tops", str(v)], capture_output=True, text=True)
    check("the dry run counts and changes nothing", "Would change 1 notes" in r.stdout and "\n# Apfelschorle" in (v / "Food/Apfelschorle.md").read_text(), r.stdout)
    r = subprocess.run([sys.executable, str(SCRIPT), "tops", str(v), "--live"], capture_output=True, text=True)
    check("the live run changes the note", (v / "Food/Apfelschorle.md").read_text() == fm + "## Notes\n", r.stdout + r.stderr)
    check("Obsidian's own folder is left alone", (v / ".obsidian/x.md").read_text().endswith("\n# x\n"))
    backups = list((v / ".icor-for-life/backups").glob("tidy-markdown-*"))
    check("the original is backed up", len(backups) == 1 and (backups[0] / "Food/Apfelschorle.md").read_text().startswith(fm + "\n# Apfelschorle"))
    r = subprocess.run([sys.executable, str(SCRIPT), "restore", str(backups[0])], capture_output=True, text=True)
    check("restore puts it back", (v / "Food/Apfelschorle.md").read_text() == fm + "\n# Apfelschorle\n\n## Notes\n", r.stdout + r.stderr)
    (v / "wrapped.md").write_text("one line\nwrapped\n", encoding="utf-8")
    r = subprocess.run([sys.executable, str(SCRIPT), "check", str(v / "wrapped.md")], capture_output=True, text=True)
    check("check fails on a hard-wrapped note", r.returncode == 1 and "FAIL" in r.stdout, r.stdout)
    r = subprocess.run([sys.executable, str(SCRIPT), "check", str(v / "Food")], capture_output=True, text=True)
    check("check passes a tidy folder", r.returncode == 0, r.stdout)

if fails:
    print("FAIL %d of %d cases" % (len(fails), checks))
    sys.exit(1)
print("OK %d cases held" % checks)
