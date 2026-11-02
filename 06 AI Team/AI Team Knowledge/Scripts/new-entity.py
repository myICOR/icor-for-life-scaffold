#!/usr/bin/env python3
"""Create one entity note from its template, in its room, already linked.

Usage:
  new-entity.py <type> "<Title>" [--link "[[Target]]"]...
  new-entity.py journal "<Title>" --journal-type thought --original "..."
  new-entity.py --list
  new-entity.py <type> "<Title>" --root <vault-root>

This is the script half of the by-hand walkthrough in
GL-1007 "Doing it by hand": right-click the room, New note, Templates:
Insert template, fill the properties, link it. The member may do every one
of those moves in Obsidian; this does the same moves with the same result,
so what the AI files and what the member files are the same note.

The frontmatter is NEVER written here. It comes from
06 AI Team/AI Team Knowledge/Templates/<type>.md, which GL-1002 names as
the one place the field list is spelled out as YAML. Adding a field means
editing GL-1002 and its template, never this file.

Guards (GL-1005: a rule a machine can check is a check, not a sentence):
  - an unknown type is refused, with the list of known ones
  - a title that breaks GL-1004 is refused (empty, a character Obsidian
    cannot put in a filename, a leading or trailing dot or space)
  - an existing note is never overwritten
  - a --link whose target does not exist in the vault is refused: a
    wikilink to nothing is the dangling_links metric, created on purpose
  - a --link whose target type has no field on this type is refused,
    naming the fields that exist
  - `note` without at least one of projects / key_elements / topics is
    refused (GL-1007: a note that links to nothing failed the Capturing
    Beast and should not exist)
  - `project` without a goal is refused (GL-1002: no project without a
    goal)
  - a --set names a field GL-1002 does not declare for this type, or a
    value outside a closed set GL-1002 states, is refused
  - a required field GL-1002 declares for this type that the template
    does not fill (note_type, doc_type, source_file) must be given with
    --set, or the note is not created: a note that fails
    validate-scaffold.py the moment it exists is not a created note
  - the room for every type is asserted against validate-scaffold.py's
    own required-folder list, so the two can never drift apart
"""
import argparse, ast, datetime, importlib.util, json, re, subprocess, sys
from pathlib import Path

# NO BYTECODE IN THE TREE WE ARE POINTED AT. This script importlib-loads a
# sibling out of Scripts/, and stock CPython then writes
# Scripts/__pycache__/<sibling>.cpython-3NN.pyc beside it, which is INSIDE the
# vault or the repo it was asked to read. A script that writes into the thing
# it measures is a script whose measurement nobody can trust, and the write is
# invisible under macOS's /usr/bin/python3, which redirects bytecode to its own
# cache (Conrad Froehling, 2026-09-16). PYTHONDONTWRITEBYTECODE is read at
# interpreter STARTUP, so only this assignment reaches a process already
# running.
sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
DEFAULT_ROOT = HERE.parents[2]
TEMPLATES = "06 AI Team/AI Team Knowledge/Templates"

# GL-1002's per-type table is parsed in one place, new-base.py, and read
# from there by every script that needs it. A second parser would be a
# second answer to "what does the guideline say".
_spec = importlib.util.spec_from_file_location("new_base", HERE / "new-base.py")
new_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(new_base)

# Same loader shape for the shared byte-safe reader and writer. A missing
# noteio-icor.py is a half-upgraded Scripts/ folder and says so in one line.
if not (HERE / "noteio-icor.py").is_file():
    raise SystemExit("FAIL noteio-icor.py is missing from %s. Scripts/ is half "
                     "upgraded; restore noteio-icor.py beside this script and run "
                     "this again." % HERE)
_nio = importlib.util.spec_from_file_location("noteio", HERE / "noteio-icor.py")
noteio = importlib.util.module_from_spec(_nio)
_nio.loader.exec_module(noteio)

# The room each entity type is filed in. Every folder here is asserted
# against validate-scaffold.py's REQUIRED list at run time (rooms_check),
# so this map cannot name a folder the scaffold does not guarantee.
ROOMS = {
    "person":      "04 Inner World/Contacts/People",
    "company":     "04 Inner World/Contacts/Companies",
    "note":        "04 Inner World/Notes",
    "document":    "04 Inner World/Notes",
    "project":     "04 Inner World/My Life/Projects",
    "goal":        "04 Inner World/My Life/Goals",
    "habit":       "04 Inner World/My Life/Habits",
    "topic":       "04 Inner World/My Life/Topics",
    "key-element": "04 Inner World/My Life/Key Elements",
    "journal":     "04 Inner World/Journal",   # delegated, see below
}

# Which frontmatter field carries a link to a target of a given type,
# per GL-1002. {new note's type: {target's type: field}}. A pair missing
# here is refused rather than guessed: putting a person in `topics` would
# pass YAML and fail meaning.
LINK_FIELDS = {
    "note":        {"project": "projects", "key-element": "key_elements",
                    "topic": "topics", "person": "people",
                    "company": "companies"},
    "document":    {"project": "projects", "key-element": "key_elements",
                    "topic": "topics", "person": "people",
                    "company": "companies"},
    "project":     {"goal": "goal", "key-element": "key_elements"},
    "goal":        {"key-element": "key_elements"},
    "key-element": {"person": "people", "goal": "goals"},
    "topic":       {"topic": "related_topics"},
    "person":      {"company": "companies"},
    "company":     {"person": "people"},
    "habit":       {"planner-habit": "planner_habit"},
}
# Fields that hold ONE wikilink rather than a list (GL-1002).
SINGLE_FIELDS = {"goal", "planner_habit"}
# Fields whose wikilink is written FULL-PATH-QUALIFIED,
# `[[02 Planner/Habits/Morning walk]]`, rather than as the bare note name
# (GL-1002 rows `habit` and `planner-habit`, ruling 2026-09-16). A habit and
# its planner-habit note carry the SAME name by design, one in
# `02 Planner/Habits/` and one in `04 Inner World/My Life/Habits/`, so a bare
# `[[Morning walk]]` cannot say which of the two it means: Obsidian resolves
# it by proximity and every other reader has to guess (Brian Carroll, B2-3).
QUALIFIED_FIELDS = {"planner_habit"}
# The link rule per type: at least one link must land in one of these
# fields, or the note has no reason to exist (GL-1007, GL-1002).
LINK_RULE = {
    "note": ("projects", "key_elements", "topics"),
    "project": ("goal",),
}
# Characters Obsidian cannot carry in a note name, plus the shapes that
# break a wikilink. GL-1004: an entity note is its natural title.
BAD_TITLE_CHARS = set('[]#^|\\/:*?"<>')


def fail(msg):
    sys.exit("FAIL " + msg)


def rooms_check(root):
    """Every folder in ROOMS must be a folder validate-scaffold.py requires.
    Read from its source, never restated: two hand-kept copies of a folder
    list disagree the first time one of them is edited."""
    src = (HERE / "validate-scaffold.py").read_text(encoding="utf-8")
    m = re.search(r"^REQUIRED = (\[.*?\])\n", src, re.S | re.M)
    if not m:
        fail("cannot read REQUIRED from validate-scaffold.py; the rooms map "
             "has nothing to check itself against")
    required = set(ast.literal_eval(m.group(1)))
    for t, folder in sorted(ROOMS.items()):
        if folder not in required:
            fail("room for %r (%s) is not in validate-scaffold.py's REQUIRED "
                 "list; fix one of the two before creating notes" % (t, folder))


def read_frontmatter(text):
    """{key: raw value string} for the top-level keys of a frontmatter
    block, plus the block's own text. Enough to read `type` and `aliases`;
    this is not a YAML parser and never needs to be."""
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}
    out = {}
    for line in text[4:end].splitlines():
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):(.*)$", line)
        if m:
            out[m.group(1)] = m.group(2).strip()
    return out


def link_target(raw):
    """The note name inside a --link value: `[[X]]`, `[[X|alias]]` or `X`."""
    s = raw.strip()
    m = re.fullmatch(r"\[\[(.+?)\]\]", s)
    if m:
        s = m.group(1)
    s = s.split("|", 1)[0].split("#", 1)[0].strip()
    return s


def find_note(root, name):
    """The one markdown file this link names, by filename stem or by an
    `aliases` entry, the way Obsidian resolves a wikilink. Returns the
    path, or None. More than one match is refused by the caller."""
    hits = []
    key = name.casefold()
    for p in root.rglob("*.md"):
        if any(part.startswith(".") for part in p.relative_to(root).parts):
            continue
        if p.stem.casefold() == key:
            hits.append(p)
            continue
        fm = read_frontmatter(p.read_text(encoding="utf-8", errors="ignore"))
        al = fm.get("aliases", "")
        if al.startswith("["):
            values = [v.strip().strip("'\"") for v in al.strip("[]").split(",")]
            if any(v.casefold() == key for v in values if v):
                hits.append(p)
    return hits


def slugify(title):
    s = re.sub(r"[^a-z0-9]+", "-", title.casefold()).strip("-")
    return s


def set_field(text, field, values):
    """Put wikilinks into one frontmatter field of the rendered template.
    The field must already be in the template: a template without it is
    drift between GL-1002 and Templates/, and is refused rather than
    patched around."""
    single = field in SINGLE_FIELDS
    if single:
        if len(values) > 1:
            fail("%s takes one link, got %d" % (field, len(values)))
        new = '%s: "[[%s]]"' % (field, values[0])
    else:
        new = "%s: [%s]" % (field, ", ".join('"[[%s]]"' % v for v in values))
    pat = re.compile(r"^%s:[ \t]*(\[\])?[ \t]*$" % re.escape(field), re.M)
    if not pat.search(text):
        fail("Templates/<type>.md has no empty %r field to fill; template and "
             "GL-1002 have drifted apart" % field)
    return pat.sub(lambda _: new, text, count=1)


# --- filling a template line ------------------------------------------------
# A template line is `field:` followed by, optionally, a default the template
# ships, and, optionally, a trailing `# comment` that says which note_type the
# field belongs to. Until 2026-09-15 only the bare `field:` shape could be
# filled, so seven of note.md's own fields (source_url, consumed, idea_status,
# transcript, transcribed_by, ai_summary, audio_retained) were unreachable
# from --set and the script reported them as drift between GL-1002 and the
# template (Ian Slattery, T15-B / Brian Carroll, T16-10).
TEMPLATE_LINE = re.compile(
    r"^(?P<field>[A-Za-z_][A-Za-z0-9_-]*):"
    r"(?P<value>[^\n#]*)"
    r"(?P<comment>#[^\n]*)?$", re.M)
# The defaults a template may ship that still mean "nobody has answered this":
# nothing, an empty list, and `false` on a boolean that only becomes true once
# the member does something.
UNANSWERED = {"", "[]", "false"}
# Which note_type each `# <type> only` comment in Templates/note.md belongs to.
# The comment in the template is the source: restating the map here would be a
# second answer to a question GL-1002 and the template already answer once.
ONLY_FOR = re.compile(r"#\s*(?P<types>[a-z][a-z ,/]*?)\s+only\b")


# A frontmatter value that is one wikilink goes in as a double-quoted string.
# Bare, `[[X]]` is a list holding a list, not a link, and Obsidian's Properties
# panel shows it as such. Only a WHOLE value that is a wikilink is quoted; every
# other value is written byte for byte. JSON is used because a JSON string is a
# valid YAML double-quoted scalar, escapes and all.
# set-property.py carries the same four lines and the fixture suite
# (test-note-scripts.py) asserts the two agree. It cannot live in
# noteio-icor.py: that file is a pinned byte-identical copy of myPKA's noteio.py.
WHOLE_WIKILINK = re.compile(r"^!?\[\[.*\]\]$")


def yaml_scalar(value):
    return json.dumps(value, ensure_ascii=False) if WHOLE_WIKILINK.match(value) else value


def template_line(text, field):
    """The whole template line for one field, or None."""
    for m in TEMPLATE_LINE.finditer(text):
        if m.group("field") == field:
            return m.group(0)
    return None


def fillable(line):
    """True while the template has not already answered this field itself."""
    m = TEMPLATE_LINE.fullmatch(line)
    return m is not None and m.group("value").strip() in UNANSWERED


def line_number(text, line):
    return text[:text.index(line)].count("\n") + 1


def render_set(field, line, value):
    """The replacement line. A field whose template default is a list is
    written as a list: `--set tags=pkm` used to land `tags: pkm`, a string
    where every reader expects a sequence (Ian Slattery, T15-B)."""
    m = TEMPLATE_LINE.fullmatch(line)
    if m.group("value").strip() == "[]":
        return '%s: ["%s"]' % (field, value)
    return "%s: %s" % (field, yaml_scalar(value))


def prune_by_note_type(text, note_type):
    """Drop the frontmatter lines a template marks `# <other type> only`.

    Templates/note.md carries the union of every note_type's fields, so a
    note copied straight from it arrives with four meeting keys, an idea key
    and two reference keys whatever it actually is. They are not invented
    fields, but they are noise in the Properties panel of every note in the
    vault (GL-1002: a field that cannot mean anything here does not belong
    here).
    """
    note_type = str(note_type).strip().strip("'\"")
    if not note_type or not text.startswith("---\n"):
        return text
    close = text.find("\n---\n", 3)
    if close == -1:
        return text
    front, rest = text[4:close], text[close:]
    out = []
    for line in front.split("\n"):
        m = TEMPLATE_LINE.fullmatch(line)
        only = ONLY_FOR.search(m.group("comment") or "") if m else None
        if only and m.group("value").strip() in UNANSWERED:
            types = {t for t in re.split(r"[ ,/]+", only.group("types")) if t}
            if note_type not in types:
                continue
        out.append(line)
    return "---\n" + "\n".join(out) + rest


def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("type", nargs="?")
    ap.add_argument("title", nargs="?")
    ap.add_argument("--link", action="append", default=[],
                    help='a note to link, "[[Target]]" or Target; repeatable')
    ap.add_argument("--set", action="append", default=[], metavar="FIELD=VALUE",
                    dest="sets", help="fill a scalar field, e.g. --set note_type=outline")
    ap.add_argument("--list", action="store_true", help="show the types and their rooms")
    ap.add_argument("--root", default=None)
    # journal only: new-entity.py hands these straight to new-journal-entry.py
    ap.add_argument("--journal-type", help="journal only: interaction|note|thought|milestone")
    ap.add_argument("--original", help="journal only: the user's exact words")
    ap.add_argument("--date", help="journal only: the entry's date (default today)")
    ap.add_argument("--format", help="journal only: voice|photo|meeting-notes|other")
    a = ap.parse_args()
    root = Path(a.root).resolve() if a.root else DEFAULT_ROOT

    if a.list:
        for t, folder in sorted(ROOMS.items()):
            print("%-12s -> %s" % (t, folder))
        return 0
    if not a.type or not a.title:
        fail("usage: new-entity.py <type> \"<Title>\" [--link \"[[X]]\"]... (or --list)")
    if a.type not in ROOMS:
        fail("unknown type %r; known types: %s" % (a.type, ", ".join(sorted(ROOMS))))

    rooms_check(root)

    title = a.title.strip()
    if not title:
        fail("empty title")
    bad = sorted(set(title) & BAD_TITLE_CHARS)
    if bad:
        fail("title breaks GL-1004: %s cannot be in a note name (%r)"
             % (" ".join(repr(c) for c in bad), title))
    if title != a.title or title.startswith(".") or title.endswith("."):
        fail("title breaks GL-1004: no leading or trailing space or dot (%r)" % a.title)
    if title.lower().endswith(".md"):
        fail("title breaks GL-1004: give the title, not the filename (%r)" % title)

    journal_only = {"--journal-type": a.journal_type, "--original": a.original,
                    "--date": a.date, "--format": a.format}
    if a.type != "journal":
        used = [k for k, v in journal_only.items() if v]
        if used:
            fail("%s only apply to `journal`" % ", ".join(sorted(used)))
    else:
        # Journal entries have their own script: the date-nested path, the
        # slug rule and the sacred Original Text section live there and are
        # not reimplemented here (GL-1003).
        if a.link or a.sets:
            fail("--link and --set do not apply to a journal entry; its fields "
                 "come from new-journal-entry.py, and linked_people / "
                 "linked_topics / linked_projects are filled on the entry")
        if not a.journal_type or not a.original:
            fail("a journal entry needs --journal-type and --original "
                 "(they go straight to new-journal-entry.py)")
        slug = slugify(title)
        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+){0,7}", slug):
            fail("title does not reduce to a GL-1004 slug: %r" % title)
        argv = [sys.executable, str(HERE / "new-journal-entry.py"),
                "--root", str(root),
                "--date", a.date or datetime.date.today().isoformat(),
                "--slug", slug, "--journal-type", a.journal_type,
                "--original", a.original]
        if a.format:
            argv += ["--format", a.format]
        return subprocess.run(argv).returncode

    folder = root / ROOMS[a.type]
    if not folder.is_dir():
        fail("room missing: %s" % ROOMS[a.type])
    dest = folder / (title + ".md")
    if dest.exists():
        fail("%s already exists; one thing, one note (open it instead)"
             % dest.relative_to(root))

    template = root / TEMPLATES / ("%s.md" % a.type)
    if not template.is_file():
        fail("no template for %r at %s/%s.md" % (a.type, TEMPLATES, a.type))

    # Resolve every link before writing anything: a half-written note with
    # one good link and one bad one is worse than no note.
    by_field = {}
    for raw in a.link:
        name = link_target(raw)
        if not name:
            fail("empty --link")
        hits = find_note(root, name)
        if not hits:
            fail("--link target does not exist: [[%s]] (create it first; a link "
                 "to nothing is a dangling link)" % name)
        if len(hits) > 1:
            fail("--link [[%s]] matches %d notes: %s"
                 % (name, len(hits),
                    ", ".join(str(h.relative_to(root)) for h in hits)))
        target = hits[0]
        tfm = read_frontmatter(target.read_text(encoding="utf-8", errors="ignore"))
        ttype = tfm.get("type", "").strip().strip("'\"")
        allowed = LINK_FIELDS.get(a.type, {})
        if ttype not in allowed:
            fail("a %s cannot link to a %s; %s links to: %s"
                 % (a.type, ttype or "note with no type", a.type,
                    ", ".join(sorted(allowed)) or "nothing"))
        field = allowed[ttype]
        # `.as_posix()`, not str(): a wikilink is forward-slashed on every
        # platform, and a Windows member would otherwise get backslashes
        # inside the brackets and a dangling link.
        by_field.setdefault(field, []).append(
            target.relative_to(root).with_suffix("").as_posix()
            if field in QUALIFIED_FIELDS else target.stem)

    rule = LINK_RULE.get(a.type)
    if rule and not any(f in by_field for f in rule):
        fail("a %s needs at least one --link landing in %s (GL-1007: a note "
             "that links to nothing should not exist)"
             % (a.type, " / ".join(rule)))

    # --set: scalar fields, checked against GL-1002 before anything is
    # written. A field the guideline does not declare for this type is the
    # invented_fields metric, created on purpose (CLAUDE.md hard rule 4).
    declared = new_base.gl002_fields(root).get(a.type, set())
    enums = new_base.gl002_enums(root).get(a.type, {})
    link_fields = set(LINK_FIELDS.get(a.type, {}).values())
    scalars = {}
    for pair in a.sets:
        if "=" not in pair:
            fail("--set takes FIELD=VALUE, got %r" % pair)
        field, value = pair.split("=", 1)
        field, value = field.strip(), value.strip()
        if field not in declared:
            fail("%r is not a GL-1002 field for type %r; declared: %s"
                 % (field, a.type, ", ".join(sorted(declared))))
        if field in link_fields or field in SINGLE_FIELDS:
            # By name, not "did a --link happen to fill it": --set can reach a
            # `field: []` line since 2026-09-15, and `--set topics=Foo` would
            # otherwise write a bare name where every reader expects
            # "[[Foo]]", which is a dangling link the moment it is saved.
            fail("%r is a link field; use --link, not --set" % field)
        if field in enums and value not in enums[field]:
            fail("%s must be one of %s (GL-1002), got %r"
                 % (field, " | ".join(enums[field]), value))
        if not value:
            fail("--set %s= has no value" % field)
        scalars[field] = value

    today = datetime.date.today()
    # The template is read from bytes and then normalised to LF on purpose: a
    # note this script creates ships LF whatever the member's template picked
    # up from a sync (Ian Slattery, T15-A).
    text = noteio.read_note(template)[0]
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = (text.replace("{{title}}", title)
                .replace("{{date}}", today.isoformat())
                .replace("{{time}}", datetime.datetime.now().strftime("%H:%M")))
    for field, values in by_field.items():
        text = set_field(text, field, values)
    for field, value in scalars.items():
        line = template_line(text, field)
        if line is None:
            fail("Templates/%s.md has no %r line to fill; template and GL-1002 "
                 "have drifted apart" % (a.type, field))
        if not fillable(line):
            fail("Templates/%s.md already fills %r on line %d and this script "
                 "does not overwrite a template's own answer:\n    %s"
                 % (a.type, field, line_number(text, line), line.strip()))
        text = text.replace(line, render_set(field, line, value), 1)

    text = prune_by_note_type(text, read_frontmatter(text).get("note_type", ""))

    # Every field GL-1002 marks required for this type must now carry a
    # value. Some arrive from the template (a project's status), some from
    # --link (its goal), the rest must come from --set.
    filled = read_frontmatter(text)
    empty = sorted(f for f in new_base.gl002_required(root).get(a.type, set())
                   if not filled.get(f, "").strip("[]\"' "))
    if empty:
        fail("%s is required for a %s and is still empty; pass %s"
             % (", ".join(empty), a.type,
                " ".join("--set %s=<value>" % f for f in empty)))

    noteio.write_note(dest, text)
    print("OK created %s" % dest.relative_to(root))
    return 0


if __name__ == "__main__":
    sys.exit(main())
