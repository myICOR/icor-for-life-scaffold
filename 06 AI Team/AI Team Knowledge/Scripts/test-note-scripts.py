#!/usr/bin/env python3
"""test-note-scripts.py: the fixture suite behind the scripts that write a
note's frontmatter (set-property, new-entity, new-journal-entry,
stamp-processed) and the reader that judges it (check-quality).

Copies this folder into a throwaway vault, runs each script from that copy
and asserts what lands on disk. GL-1005 rule 4: a guard nobody has watched go
red is not a guard, so every "still refused" and "still reported" case here
is an input the script must say no to.

Run it with --break-me to prove the suite itself can go red: it flips one
assertion's expectation and the run must end in FAIL.

Usage:  test-note-scripts.py [--break-me]
Exit 0 = every case held. Exit 1 = a case did not.
"""
import importlib.util, json, shutil, subprocess, sys, tempfile
from pathlib import Path

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SCRIPTS = "06 AI Team/AI Team Knowledge/Scripts"
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


def fresh(tmp, name):
    """A vault with the shipped rooms and scripts and nothing of myPKA's."""
    vault = Path(tmp) / name
    shutil.copytree(ROOT, vault, symlinks=True,
                    ignore=shutil.ignore_patterns(".git", ".obsidian", "__pycache__", ".mypka"))
    (vault / SCRIPTS / "resolve.py").unlink(missing_ok=True)
    return vault


def run(vault, script, *args):
    return subprocess.run([PY, str(vault / SCRIPTS / script), *map(str, args)],
                          capture_output=True, text=True, encoding="utf-8")


def write(vault, rel, text):
    p = vault / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(text.encode("utf-8"))
    return p


def frontmatter_line(path, field):
    for line in path.read_bytes().decode("utf-8").splitlines():
        if line.startswith(field + ":"):
            return line
    return None


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def no_traceback(r):
    return "Traceback" not in r.stderr


def findings_for(vault, rel):
    r = run(vault, "check-quality.py", vault, "--json")
    return [f for f in json.loads(r.stdout)["findings"] if f.get("path") == rel]


def set_property_cases(tmp):
    print("set-property.py")
    v = fresh(tmp, "sp")
    note = write(v, "04 Inner World/My Life/Habits/Walk.md", "---\ntype: habit\n---\n\nBody\n")
    link = "[[02 Planner/Habits/Morning walk]]"
    r = run(v, "set-property.py", note, "planner_habit", link, "--root", v)
    check("a wikilink value lands double-quoted",
          frontmatter_line(note, "planner_habit") == 'planner_habit: "%s"' % link,
          repr(frontmatter_line(note, "planner_habit")) + r.stderr)
    CQ = load("cq_sp", v / SCRIPTS / "check-quality.py")
    front = CQ.split_front(note.read_text(encoding="utf-8"))[0]
    check("the reader gets a string equal to the wikilink",
          CQ.parse_front(front).get("planner_habit") == link)
    try:
        import yaml
    except ImportError:
        print("  skip a YAML library agrees: no PyYAML here")
    else:
        check("a YAML library agrees", yaml.safe_load(front).get("planner_habit") == link)
    r = run(v, "set-property.py", note, "planner_habit", link, "--root", v)
    check("the same value again is already there", "already" in r.stdout, r.stdout)

    note = write(v, "04 Inner World/My Life/Habits/Old.md",
                 "---\ntype: habit\nplanner_habit: %s\n---\n" % link)
    run(v, "set-property.py", note, "planner_habit", link, "--root", v)
    check("a bare link an older version wrote is repaired",
          frontmatter_line(note, "planner_habit") == 'planner_habit: "%s"' % link,
          repr(frontmatter_line(note, "planner_habit")))

    note = write(v, "04 Inner World/My Life/Habits/Embed.md", "---\ntype: habit\n---\n")
    run(v, "set-property.py", note, "planner_habit", "![[x.png]]", "--root", v)
    check("an embed is quoted too",
          frontmatter_line(note, "planner_habit") == 'planner_habit: "![[x.png]]"')

    note = write(v, "04 Inner World/My Life/Habits/Crlf.md", "---\r\ntype: habit\r\n---\r\nBody\r\n")
    run(v, "set-property.py", note, "planner_habit", link, "--root", v)
    check("a CRLF note keeps its line endings",
          note.read_bytes() == ('---\r\ntype: habit\r\nplanner_habit: "%s"\r\n---\r\nBody\r\n'
                                % link).encode("utf-8"), repr(note.read_bytes()))

    note = write(v, "04 Inner World/My Life/Habits/Plain.md", "---\ntype: habit\n---\n")
    for value in ("active", "see [[A]] and more", "[[A]] and more", "[a, b]", '"already quoted"'):
        run(v, "set-property.py", note, "name", value, "--root", v)
        check("a non-wikilink value is written byte for byte: %s" % value,
              frontmatter_line(note, "name") == "name: %s" % value,
              repr(frontmatter_line(note, "name")))


def new_entity_cases(tmp):
    print("new-entity.py")
    v = fresh(tmp, "ne")
    write(v, "05 Assets/Documents/Example Invoice.pdf", "pdf")
    r = run(v, "new-entity.py", "document", "Test contract", "--set", "doc_type=contract",
            "--set", "source_file=[[Example Invoice.pdf]]", "--link", "[[Health]]", "--root", v)
    note = v / "04 Inner World/Notes/Test contract.md"
    check("--set with a wikilink lands double-quoted", note.is_file() and
          frontmatter_line(note, "source_file") == 'source_file: "[[Example Invoice.pdf]]"',
          r.stdout + r.stderr)
    check("--set with a plain value stays bare",
          note.is_file() and frontmatter_line(note, "doc_type") == "doc_type: contract")
    text = note.read_text(encoding="utf-8") if note.is_file() else ""
    check("--link is unchanged", '- "[[Health]]"' in text or '["[[Health]]"]' in text, text[:300])
    SP = load("sp_ne", v / SCRIPTS / "set-property.py")
    NE = load("ne_ne", v / SCRIPTS / "new-entity.py")
    same = all(SP.yaml_scalar(s) == NE.yaml_scalar(s)
               for s in ("[[A]]", "![[A.png]]", 'x "y"', "[[a]] b", '[[a"b]]', "[[Ü]]", "plain"))
    check("set-property and new-entity carry the same yaml_scalar", same)


def journal_cases(tmp):
    print("new-journal-entry.py")
    v = fresh(tmp, "nj")
    r = run(v, "new-journal-entry.py", "--date", "2024-03-05", "--slug", "old-entry",
            "--journal-type", "thought", "--original", "words", "--root", v)
    note = v / "04 Inner World/Journal/2024/03/2024-03-05_old-entry.md"
    check("--date drives created", note.is_file() and
          frontmatter_line(note, "created") == "created: 2024-03-05", r.stdout + r.stderr)
    check("--date still drives date",
          note.is_file() and frontmatter_line(note, "date") == "date: 2024-03-05")
    check("a journal entry carries no invented field",
          not [f for f in findings_for(v, note.relative_to(v).as_posix())
               if f.get("metric") == "invented_fields"])


def stamp_name_cases(tmp):
    print("stamp-processed.py, the name of a scratchpad")
    v = fresh(tmp, "sn")
    room = "00 Daily Scratchpad/2026/11/"
    for name, want in (("202611021215.md", "2026-11-02"),
                       ("202611021215 2.md", "2026-11-02"),
                       ("202611021215 - a title.md", "2026-11-02"),
                       ("20261102121530.md", "2026-11-02"),
                       ("2026-11-02.md", "2026-11-02"),
                       ("2026-11-02-121530.md", "2026-11-02")):
        note = write(v, room + name, "typed\n")
        r = run(v, "stamp-processed.py", note, "--summary", "s", "--into", "[[Health]]")
        check("%s stamps with date %s" % (name, want),
              r.returncode == 0 and frontmatter_line(note, "date") == "date: " + want,
              r.stdout + r.stderr)
        check("%s becomes a scratchpad" % name,
              frontmatter_line(note, "type") == "type: scratchpad")
    for name in ("202613451215.md", "202602301215.md", "202611022561.md", "2026-13-45.md",
                 "1234567890123456.md", "my notes.md"):
        note = write(v, room + name, "typed\n")
        r = run(v, "stamp-processed.py", note, "--summary", "s", "--into", "[[Health]]")
        check("%s is still refused" % name,
              r.returncode == 1 and r.stderr.startswith("FAIL") and no_traceback(r)
              and note.read_text(encoding="utf-8") == "typed\n", r.stdout + r.stderr)


def capture_fixture(v, name, folder="Scanner Inbox"):
    data = b"%PDF " + name.encode("utf-8")
    cap = v / "01 Inbox" / folder / name
    cap.parent.mkdir(parents=True, exist_ok=True)
    cap.write_bytes(data)
    (v / "05 Assets/Documents").mkdir(parents=True, exist_ok=True)
    (v / "05 Assets/Documents" / name).write_bytes(data)
    note = write(v, "04 Inner World/Notes/%s wrapper.md" % name,
                 '---\ntype: document\ndoc_type: other\nsource_file: "[[%s]]"\n---\n' % name)
    return note, cap


def stamp_capture_cases(tmp):
    print("stamp-processed.py, --capture")
    v = fresh(tmp, "sc")
    for label, name, ref in (("a plain path", "a.pdf", None),
                             ("the slot form", "b.pdf", "concept:inbox/scanner/b.pdf"),
                             ("the folder-name form", "c.pdf", "concept:inbox/Scanner Inbox/c.pdf")):
        note, cap = capture_fixture(v, name)
        r = run(v, "stamp-processed.py", note, "--summary", "filed", "--into", "[[Health]]",
                "--capture", ref or cap)
        check("%s stamps the note and clears the inbox" % label,
              r.returncode == 0 and not cap.exists()
              and frontmatter_line(note, "processed") == "processed: true", r.stdout + r.stderr)
    note, cap = capture_fixture(v, "ow.pdf", "Outer World")
    r = run(v, "stamp-processed.py", note, "--summary", "filed", "--into", "[[Health]]",
            "--capture", "concept:inbox/outer_world/ow.pdf")
    check("the outer_world slot resolves", r.returncode == 0 and not cap.exists(), r.stderr)

    note, cap = capture_fixture(v, "d.pdf")
    for ref in ("concept:nosuch/d.pdf", "concept:", "concept:notes/d.pdf",
                "concept:inbox/../../secret.pdf", "concept:inbox/scanner/missing.pdf"):
        r = run(v, "stamp-processed.py", note, "--summary", "filed", "--into", "[[Health]]",
                "--capture", ref)
        check("%s is a FAIL line and touches nothing" % ref,
              r.returncode == 1 and r.stderr.startswith("FAIL") and no_traceback(r)
              and cap.exists() and frontmatter_line(note, "processed") is None,
              r.stdout + r.stderr)

    # Where myPKA shares the folder its resolver decides, so a member's own
    # home is honoured; a stub stands in for it here because this suite runs
    # in the public Scaffold too.
    v = fresh(tmp, "sr")
    note, cap = capture_fixture(v, "e.pdf", "My Scans")
    write(v, SCRIPTS + "/resolve.py",
          "from pathlib import Path\n"
          "HERE = Path(__file__).resolve().parents[3]\n"
          "class ResolveError(Exception):\n    pass\n"
          "def load(root):\n    return root\n"
          "def resolve_ref(ref, **kw):\n"
          "    if ref.endswith('bad.pdf'):\n"
          "        raise ResolveError('E_UNKNOWN_CONCEPT nosuch: not a concept')\n"
          "    return Path(kw['bindings']) / '01 Inbox/My Scans' / ref.rsplit('/', 1)[1]\n")
    r = run(v, "stamp-processed.py", note, "--summary", "filed", "--into", "[[Health]]",
            "--capture", "concept:inbox/scanner/bad.pdf")
    check("a resolver refusal is a FAIL line, not a traceback",
          r.returncode == 1 and "E_UNKNOWN_CONCEPT" in r.stderr and no_traceback(r), r.stderr)
    r = run(v, "stamp-processed.py", note, "--summary", "filed", "--into", "[[Health]]",
            "--capture", "concept:inbox/scanner/e.pdf")
    check("resolve.py beside the script decides", r.returncode == 0 and not cap.exists(),
          r.stdout + r.stderr)


def quality_cases(tmp):
    print("check-quality.py")
    v = fresh(tmp, "cq")
    head = ('---\ntype: pdf-highlight\nhighlight_id: h1\nsource_file: "[[paper.pdf]]"\npage: 1\n'
            "anchor: rect\nrects: %s\ncolor: yellow\ncreated: 2026-11-02\n"
            'canvases: []\nlinked_notes: []\ncssclasses: [icor-pdf-highlight]\n---\n\n%s\n')
    write(v, "05 Assets/Documents/paper.pdf", "pdf")
    one = "04 Inner World/Notes/Highlights/one.md"
    many = "04 Inner World/Notes/Highlights/many.md"
    write(v, one, head % ("[[72.5, 400, 300, 520]]", "> a quote"))
    write(v, many, head % ("[[72.5, 400, 300, 520], [72.5, 380, 300, 396]]", "See [[Missing note]]."))
    dangling = lambda rel: [f for f in findings_for(v, rel) if f.get("metric") == "dangling_links"]
    check("one rect is no dangling link", not dangling(one), str(dangling(one)))
    got = dangling(many)
    check("a real dangling link beside two rects is still reported",
          len(got) == 1 and "Missing note" in got[0]["message"], str(got))

    q = "04 Inner World/Notes/quoted.md"
    write(v, q, '---\ntype: note\nnote_type: other\ntopics: ["[[Gone topic]]"]\n---\n\ntext\n')
    check("a quoted frontmatter link to nothing is still reported",
          [f for f in dangling(q) if "Gone topic" in f["message"]], str(dangling(q)))

    CQ = load("cq_cq", v / SCRIPTS / "check-quality.py")
    LS = load("ls_cq", v / SCRIPTS / "life-snapshot.py")
    for raw, want in (("idea_status: open   # x", "open"),
                      ('k: "a # b"', "a # b"),
                      ("k: 'a # b'", "a # b"),
                      ('k: "a \\" # b" # c', 'a \\" # b'),
                      ("k: 'it''s # b' # c", "it''s # b"),
                      ("k: it's # b", "it's"),
                      ("k: a#b", "a#b"),
                      ("k: https://x.y/#z", "https://x.y/#z"),
                      ("k: [[Note#Heading]]", ["[Note#Heading]"]),
                      ('k: ["a # b", c] # d', ["a # b", "c"]),
                      ("k: # only a comment\n  - one\n  - two # x", ["one", "two"])):
        got = CQ.parse_front(raw)
        got = got.get("idea_status", got.get("k"))
        check("parse_front reads %r" % raw, got == want, repr(got))
        check("life-snapshot's fallback agrees on %r" % raw,
              LS._fb_parse_front(raw) == CQ.parse_front(raw), repr(LS._fb_parse_front(raw)))

    # Any note nothing links to yet is an orphan, whatever made it, so the
    # vault links to these two the way a member would.
    write(v, "04 Inner World/My Life/Key Elements/Ideas.md",
          "---\ntype: key-element\n---\n\n[[My idea]], [[Inline]]\n")
    idea = "04 Inner World/Notes/My idea.md"
    (v / idea).write_bytes((v / "06 AI Team/AI Team Knowledge/Templates/idea.md").read_bytes())
    check("a note made from the idea template has no findings",
          not findings_for(v, idea), str(findings_for(v, idea)))
    check("the idea template's idea_status is a clean enum",
          CQ.parse_front(CQ.split_front((v / idea).read_text(encoding="utf-8"))[0])
          .get("idea_status") == "open")
    note = "04 Inner World/Notes/Inline.md"
    write(v, note, '---\ntype: note\nnote_type: idea\nidea_status: open   # open | parked\n'
                   'key_elements:                # the link rule\n  - "[[Health]]"\n---\n')
    check("an inline comment is no enum violation and hides no list",
          not findings_for(v, note), str(findings_for(v, note)))

    chat = "00 Daily Scratchpad/2026/11/202611021215.md"
    write(v, chat, '---\ntype: scratchpad\ndate: 2026-11-02\nsource: icor-chat\n'
                   'session_ids: ["abc"]\nprocessed: true\nprocessed_summary: "s"\n'
                   'processed_into:\n  - "[[Health]]"\n---\n\nreply\n')
    check("a note saved from Chat carries no invented field",
          not [f for f in findings_for(v, chat) if f.get("metric") == "invented_fields"],
          str(findings_for(v, chat)))
    plant = chat.replace("1215", "1216")
    write(v, plant, "---\ntype: scratchpad\ndate: 2026-11-02\nsessionids: []\n---\n")
    check("a field GL-1002 does not name is still invented",
          [f for f in findings_for(v, plant) if f.get("metric") == "invented_fields"],
          str(findings_for(v, plant)))


def gitignore_case(tmp):
    print(".gitignore")
    repo = Path(tmp) / "ignore"
    repo.mkdir()
    shutil.copy(ROOT / ".gitignore", repo / ".gitignore")
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    r = subprocess.run(["git", "check-ignore", ".mypka/state/session.json"], cwd=repo,
                       capture_output=True, text=True)
    check("myPKA's session state is ignored", r.returncode == 0, r.stderr)


def main():
    with tempfile.TemporaryDirectory(prefix="test-note-scripts.") as tmp:
        set_property_cases(tmp)
        new_entity_cases(tmp)
        journal_cases(tmp)
        stamp_name_cases(tmp)
        stamp_capture_cases(tmp)
        quality_cases(tmp)
        gitignore_case(tmp)
    if BREAK:
        check("--break-me: this assertion is wrong on purpose", False, "as planned")
    if fails:
        print("FAIL %d of %d cases" % (len(fails), checks))
        return 1
    print("OK %d cases held" % checks)
    return 0


if __name__ == "__main__":
    sys.exit(main())
