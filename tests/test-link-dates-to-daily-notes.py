#!/usr/bin/env python3
"""test-link-dates-to-daily-notes.py: the red tests for GL-1011's guard.

Builds a throwaway vault in a temp folder, one fixture per rule the script
claims, and asserts the script says what it claims. GL-1005 rule 4: a gate
nobody has watched go red is not a gate, so every IGNORE fixture here is a
date the script must NOT touch, and the suite fails if it touches one.

Run it with --break-me to prove the suite itself can go red: it flips one
assertion's expectation and the run must end in FAIL.

Usage:  test-link-dates-to-daily-notes.py [--break-me]
Exit 0 = every case held. Exit 1 = a case did not.
"""
import json, re, shutil, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent / "_System" / "Tools"
SCRIPT = HERE / "link-dates-to-daily-notes.py"
PY = sys.executable
BREAK = "--break-me" in sys.argv[1:]

fails = []
checks = 0


def check(name, ok, detail=""):
    global checks
    checks += 1
    if ok:
        print(f"  ok   {name}")
    else:
        fails.append(f"{name}: {detail}")
        print(f"  FAIL {name}: {detail}")


def build(root: Path):
    """A minimal vault: the rooms the script needs, plus one fixture file
    per rule."""
    (root / ".obsidian").mkdir(parents=True)
    (root / ".obsidian" / "daily-notes.json").write_text(json.dumps(
        {"folder": "00 Daily Scratchpad", "format": "YYYY/MM/YYYY-MM-DD"}),
        encoding="utf-8")
    for d in ("00 Daily Scratchpad", "04 Inner World/Notes",
              "06 AI Team/AI Team Knowledge/Session Logs",
              "06 AI Team/AI Team Knowledge/Templates",
              "06 AI Team/Agents/Silas/journal"):
        (root / d).mkdir(parents=True, exist_ok=True)

    # 3.0: a 2.x 03 WiP left in a migrated folder is nobody's room any more; its dates are not linked
    write(root, "03 WiP/Projects/draft.md", "Drafted on 2026-09-13.\n")

    write(root, "04 Inner World/Notes/bare.md",
          "---\ncreated: 2026-01-05\ndue: 2026-01-06\n---\n"
          "We met on 2026-09-11 and again on 2026-09-12.\n")

    write(root, "04 Inner World/Notes/code.md",
          "Prose has none here.\n\n```python\nd = '2026-03-04'\n```\n"
          "And inline `2026-03-05` stays code.\n")

    write(root, "04 Inner World/Notes/tokens.md",
          "See [[2026-09-11-jeff-meyers-stood-up]] and "
          "[[2026-09-11]] already linked.\n"
          "Stamp 2026-09-11T14:12 and id tsk-2026-09-09-020 and "
          "run 2026-09-11-14-30 stay bare.\n"
          "The file 2026-09-11.md and the path Journal/2026/09 stay bare.\n"
          "A link https://example.com/blog/2026-09-11/post stays bare.\n"
          "A markdown [2026-09-11](./x.md) stays bare.\n")

    write(root, "04 Inner World/Notes/invalid.md",
          "Not a date: 2026-13-45 and 2026-02-30 are both impossible.\n")

    write(root, "04 Inner World/Notes/collides.md",
          "The meeting on 2026-07-04 is the one.\n")
    write(root, "04 Inner World/Notes/2026-07-04.md", "A note that stole the name.\n")

    # Out of scope: ALL of 06 AI Team/. The daily note is a timeline of the
    # user's life, not of the team's housekeeping, so none of these three
    # may be touched and none may create a daily note.
    write(root, "06 AI Team/AI Team Knowledge/Session Logs/2026/09/log.md",
          "Session on 2026-09-11.\n")
    write(root, "06 AI Team/AI Team Knowledge/Templates/journal.md",
          "Template date 2026-09-11.\n")
    write(root, "06 AI Team/Agents/Silas/journal/entry.md",
          "Shipped on 2026-08-01.\n")
    # Out of scope: 01 Inbox/. Every file there is a capture or an archived
    # capture, and hard rule 1 says a capture is never edited (member report
    # on 2.2.1, item 1).
    write(root, "01 Inbox/Outer World/clip.md",
          "Kept because of the talk on 2026-08-01.\n")
    write(root, "01 Inbox/Outer World/archive/2026-08-27-obsidian-video-clip.md",
          "---\ntype: capture\n---\nReleased 2026-08-20.\n")

    # Protected text inside a room that IS in scope. The Original Text
    # section of a journal entry and every blockquote stay as written; the
    # Expansion after it, and prose around a quote, still get their links.
    write(root, "04 Inner World/Journal/2026/08/2026-08-27_entry.md",
          "---\ntype: journal\n---\n\n## Original Text\n\n"
          "Call the bank on 2026-12-01.\n\n"
          "### A sub-heading the user typed\n\nStill mine: 2026-12-02.\n\n"
          "## Expansion\n\nThe call is on 2026-12-03.\n")
    write(root, "04 Inner World/Journal/2026/08/2026-08-28_tail.md",
          "## Expansion\n\nLinked: 2026-12-04.\n\n"
          "## original text\n\nTo the end of the note: 2026-12-05.\n")
    write(root, "04 Inner World/Notes/quote.md",
          "Before the quote, 2026-12-06.\n\n"
          "> Released 2026-12-07.\n"
          "lazy continuation of the quote, 2026-12-08.\n"
          "  > indented quote, 2026-12-09.\n\n"
          "After the quote, 2026-12-10.\n\n"
          "```\n## Original Text\n```\n\nAfter a fenced heading, 2026-12-11.\n")

    # A date already written as a link whose daily note is missing: no
    # rewrite to do, but the note behind it still has to be created.
    write(root, "04 Inner World/Notes/prelinked.md",
          "Booked for [[2026-10-20]] and [[2026-10-21|that Tuesday]].\n")

    # Line endings are the member's, not the script's. A CRLF note and a
    # note with a stray lone CR in the body must come back out of --fix with
    # every byte except the two pairs of brackets untouched.
    write(root, "04 Inner World/Notes/crlf.md",
          "---\r\ntype: note\r\n---\r\nSigned on 2026-06-01 in Madrid.\r\n"
          "A second line.\r\n")
    write(root, "04 Inner World/Notes/stray-cr.md",
          "Filed on 2026-06-02.\nA line with a \r stray carriage return.\n")

    # The daily note that already exists; the others must be created.
    write(root, "00 Daily Scratchpad/2026/09/2026-09-11.md", "")


def write(root, rel, text):
    """Bytes, never write_text(). On Windows text mode turns every "\n" in a
    fixture into "\r\n", so the CRLF cases below would have been testing the
    platform instead of the script (Ian Slattery, T15-A)."""
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(text.encode("utf-8"))


def run(root, *args):
    r = subprocess.run([PY, str(SCRIPT), str(root), *args],
                       capture_output=True, text=True)
    return r


def run_json(root, *args):
    r = run(root, *args, "--json")
    try:
        return r, json.loads(r.stdout)
    except ValueError:
        return r, {"items": [], "collisions": {}, "_stdout": r.stdout,
                   "_stderr": r.stderr}


with tempfile.TemporaryDirectory() as td:
    V = Path(td) / "vault"
    V.mkdir()
    build(V)

    print("check mode")
    r, rep = run_json(V, "--check")
    found = {(i["file"], i["date"]) for i in rep["items"]}

    check("check exits 1 when mentions exist", r.returncode == 1,
          f"exit {r.returncode}")
    check("bare date in body is flagged",
          ("04 Inner World/Notes/bare.md", "2026-09-11") in found
          and ("04 Inner World/Notes/bare.md", "2026-09-12") in found,
          str(sorted(found)))
    check("frontmatter date is ignored",
          not any(d in ("2026-01-05", "2026-01-06") for _f, d in found))
    check("fenced and inline code ignored",
          not any(f.endswith("code.md") for f, _d in found))
    check("token shapes ignored (slug, wikilink, ISO stamp, id, file, url, md link)",
          not any(f.endswith("tokens.md") for f, _d in found),
          str(sorted(f for f, _d in found if f.endswith("tokens.md"))))
    check("impossible dates ignored",
          not any(f.endswith("invalid.md") for f, _d in found))
    check("collision is reported", "2026-07-04" in rep["collisions"],
          str(rep["collisions"]))
    check("collision date is not linked",
          not any(d == "2026-07-04" for _f, d in found))
    check("all of 06 AI Team/ is out of scope (session log, template, agent journal)",
          not any(f.startswith("06 AI Team/") for f, _d in found),
          str(sorted(f for f, _d in found if f.startswith("06 AI Team/"))))
    check("a leftover 03 WiP is out of scope",
          not any(f.startswith("03 WiP/") for f, _d in found),
          str(sorted(f for f, _d in found if f.startswith("03 WiP/"))))
    check("01 Inbox is out of scope, archive included (hard rule 1)",
          not any(f.startswith("01 Inbox/") for f, _d in found),
          str(sorted(f for f, _d in found if f.startswith("01 Inbox/"))))
    found_dates = {d for _f, d in found}
    check("the Original Text section is never touched, sub-headings included",
          not {"2026-12-01", "2026-12-02"} & found_dates, str(sorted(found_dates)))
    check("the Expansion after Original Text is still linked",
          ("04 Inner World/Journal/2026/08/2026-08-27_entry.md", "2026-12-03") in found)
    check("an Original Text section runs to the end of the note, any case",
          "2026-12-05" not in found_dates
          and ("04 Inner World/Journal/2026/08/2026-08-28_tail.md", "2026-12-04") in found)
    check("blockquotes are never touched (lazy continuation and indent too)",
          not {"2026-12-07", "2026-12-08", "2026-12-09"} & found_dates,
          str(sorted(found_dates)))
    check("prose around a quote, and after a fenced heading, is still linked",
          {("04 Inner World/Notes/quote.md", d)
           for d in ("2026-12-06", "2026-12-10", "2026-12-11")} <= found)

    print("since filter")
    _r, rep_since = run_json(V, "--check", "--since", "2026-09-01")
    check("--since drops earlier dates",
          all(i["date"] >= "2026-09-01" for i in rep_since["items"])
          and any(i["date"] == "2026-09-11" for i in rep_since["items"]))

    print("dry-run writes nothing")
    before = {p: p.read_bytes() for p in V.rglob("*.md")}
    _r, rep_dry = run_json(V, "--dry-run")
    after = {p: p.read_bytes() for p in V.rglob("*.md")}
    check("dry-run leaves every byte alone", before == after)
    check("dry-run counts what fix would do",
          rep_dry["mentions"] == rep["mentions"]
          and rep_dry["daily_notes_created"] > 0)

    print("fix")
    r_fix, rep_fix = run_json(V, "--fix")
    body = (V / "04 Inner World/Notes/bare.md").read_text(encoding="utf-8")
    check("fix wrote the links",
          "[[2026-09-11]]" in body and "[[2026-09-12]]" in body, body)
    check("fix left frontmatter bare",
          "created: 2026-01-05\n" in body and "[[2026-01-05]]" not in body)
    check("fix created the missing daily note with its folders",
          (V / "00 Daily Scratchpad/2026/09/2026-09-12.md").is_file()
          and (V / "00 Daily Scratchpad/2026/12/2026-12-03.md").is_file())
    check("fix did not touch the agent journal",
          (V / "06 AI Team/Agents/Silas/journal/entry.md")
          .read_text(encoding="utf-8") == "Shipped on 2026-08-01.\n")
    check("created daily notes are empty",
          (V / "00 Daily Scratchpad/2026/09/2026-09-12.md").read_text() == "")
    check("an already-linked date still gets its daily note",
          (V / "00 Daily Scratchpad/2026/10/2026-10-20.md").is_file()
          and (V / "00 Daily Scratchpad/2026/10/2026-10-21.md").is_file())
    check("an already-linked file is not rewritten",
          (V / "04 Inner World/Notes/prelinked.md").read_text(encoding="utf-8")
          == "Booked for [[2026-10-20]] and [[2026-10-21|that Tuesday]].\n")
    check("fix did not touch the out-of-scope session log",
          (V / "06 AI Team/AI Team Knowledge/Session Logs/2026/09/log.md")
          .read_text(encoding="utf-8") == "Session on 2026-09-11.\n")
    check("fix did not touch the inbox capture or its archive",
          (V / "01 Inbox/Outer World/clip.md").read_text(encoding="utf-8")
          == "Kept because of the talk on 2026-08-01.\n"
          and "[[" not in (V / "01 Inbox/Outer World/archive/"
                                "2026-08-27-obsidian-video-clip.md")
                          .read_text(encoding="utf-8"))
    journal = (V / "04 Inner World/Journal/2026/08/2026-08-27_entry.md"
               ).read_text(encoding="utf-8")
    check("fix left Original Text verbatim and linked the Expansion",
          "Call the bank on 2026-12-01.\n" in journal
          and "Still mine: 2026-12-02.\n" in journal
          and "The call is on [[2026-12-03]].\n" in journal, journal)
    quote = (V / "04 Inner World/Notes/quote.md").read_text(encoding="utf-8")
    check("fix left the blockquote verbatim",
          "> Released 2026-12-07.\nlazy continuation of the quote, 2026-12-08.\n"
          in quote and "Before the quote, [[2026-12-06]]." in quote, quote)
    check("fix did not touch the code fence",
          "[[2026-03-04]]" not in
          (V / "04 Inner World/Notes/code.md").read_text(encoding="utf-8"))

    print("line endings")
    crlf = (V / "04 Inner World/Notes/crlf.md").read_bytes()
    check("a CRLF note keeps every CRLF",
          crlf == b"---\r\ntype: note\r\n---\r\nSigned on [[2026-06-01]] in "
                  b"Madrid.\r\nA second line.\r\n", repr(crlf))
    stray = (V / "04 Inner World/Notes/stray-cr.md").read_bytes()
    check("a stray lone CR in the body survives",
          stray == b"Filed on [[2026-06-02]].\nA line with a \r stray "
                   b"carriage return.\n", repr(stray))
    created = (V / "00 Daily Scratchpad/2026/06/2026-06-01.md").read_bytes()
    check("a created daily note carries no CR at all", b"\r" not in created,
          repr(created))

    print("--path scoping")
    V4 = Path(td) / "scoped"
    shutil.copytree(V, V4)
    write(V4, "04 Inner World/Notes/one.md", "Scoped 2026-05-01.\n")
    write(V4, "04 Inner World/Notes/two.md", "Untouched 2026-05-02.\n")
    before_two = (V4 / "04 Inner World/Notes/two.md").read_bytes()
    r_scope = run(V4, "--fix", "--path", "04 Inner World/Notes/one.md")
    check("--path exits 0", r_scope.returncode == 0,
          r_scope.stdout + r_scope.stderr)
    check("--path linked the file it was given",
          b"[[2026-05-01]]" in (V4 / "04 Inner World/Notes/one.md").read_bytes())
    check("--path left every other note alone",
          (V4 / "04 Inner World/Notes/two.md").read_bytes() == before_two)
    check("--path created only its own daily note",
          (V4 / "00 Daily Scratchpad/2026/05/2026-05-01.md").is_file()
          and not (V4 / "00 Daily Scratchpad/2026/05/2026-05-02.md").exists())
    r_inbox = run(V4, "--fix", "--path", "01 Inbox/Outer World/clip.md")
    check("--path on an inbox capture says it is out of scope and writes nothing",
          r_inbox.returncode == 0 and "out of the linker's scope" in r_inbox.stderr
          and b"[[" not in (V4 / "01 Inbox/Outer World/clip.md").read_bytes(),
          r_inbox.stdout + r_inbox.stderr)
    r_bad = run(V4, "--check", "--path", "nowhere/at/all.md")
    check("--path refuses a path that is not there", r_bad.returncode == 2,
          f"exit {r_bad.returncode}")

    print("idempotency")
    snap = {p: p.read_bytes() for p in V.rglob("*.md")}
    run(V, "--fix")
    check("second --fix changes nothing",
          {p: p.read_bytes() for p in V.rglob("*.md")} == snap)
    r_after = run(V, "--check")
    check("--check is green after --fix (bar the collision)",
          r_after.returncode == 0, r_after.stdout + r_after.stderr)

    print("refusals")
    V2 = Path(td) / "no-config"
    shutil.copytree(V, V2)
    (V2 / ".obsidian" / "daily-notes.json").unlink()
    r_nc = run(V2, "--fix")
    check("--fix refuses without daily-notes.json", r_nc.returncode == 2,
          f"exit {r_nc.returncode}")
    r_nc2 = run(V2, "--check")
    check("--check warns and falls back instead of refusing",
          r_nc2.returncode in (0, 1) and "WARNING" in r_nc2.stderr,
          r_nc2.stderr)

    V3 = Path(td) / "bad-format"
    shutil.copytree(V, V3)
    (V3 / ".obsidian" / "daily-notes.json").write_text(
        json.dumps({"folder": "00 Daily Scratchpad", "format": "DD-MM-YYYY"}),
        encoding="utf-8")
    r_bf = run(V3, "--check")
    check("a format that cannot back a [[YYYY-MM-DD]] link is refused",
          r_bf.returncode == 2 and "YYYY-MM-DD" in r_bf.stderr, r_bf.stderr)

    if BREAK:
        check("DELIBERATE: frontmatter date must be flagged (it must not be)",
              any(d == "2026-01-05" for _f, d in found),
              "the suite is proving it can go red")

print()
if fails:
    print(f"FAIL {len(fails)} of {checks} cases", file=sys.stderr)
    for f in fails:
        print("  " + f, file=sys.stderr)
    sys.exit(1)
print(f"OK {checks} cases held")
sys.exit(0)
