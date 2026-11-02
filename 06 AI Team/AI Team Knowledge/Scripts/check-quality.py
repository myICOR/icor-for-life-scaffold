#!/usr/bin/env python3
"""Measure the quality of what is in the vault, by hand or by AI.

Usage:
  check-quality.py [<vault-root>] [--json] [--write]

  (no flag)  one line per metric, then the findings, for a person
  --json     the whole report on stdout, for a machine
  --write    the same report to .icor-for-life/scripts/quality.json, which
             the ICOR for Life - Scaffold Check plugin reads and renders

validate-scaffold.py answers "is this a scaffold": rooms, names, shapes.
This answers "is what is IN it any good": links, enums, required fields,
invented fields, orphans, dangling links, the queues that are backing up.
Two questions, two scripts, on purpose (GL-1005): a structure failure
stops a release, a quality finding is a conversation with the member.

Everything the guideline states is READ from the guideline. The field
lists, the required fields and the closed value sets all come from
GL-1002's own table (and GL-1015's team rows, when myPKA shares this
folder) through new-base.py's parser, so a ruling changes one markdown
table and this script changes with it. What lives here is only
what GL-1002 cannot state: the thresholds below, and how a metric is
counted.

The report shape is schema 1, documented in Scripts/README.md, and is a
contract with the plugin: ids, order and field names do not change inside
a schema version.

Exit 0 = the report was produced (read `health` for the verdict).
Exit 1 = refused: the path is not a scaffold, or the report cannot be
written. A missing report is never a green.
"""
import argparse, datetime, importlib.util, json, re, sys, time
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

_spec = importlib.util.spec_from_file_location("new_base", HERE / "new-base.py")
new_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(new_base)

SCHEMA = 1

# The thresholds. `attention` is the value at which a metric stops being
# green, `broken` the value at which it needs the member today. Both are
# "this many or more". They are judgement, which is why they are here and
# not in GL-1002, and they are in ONE place so a member can move them.
THRESHOLDS = {
    # one note filed under nothing is already worth a question
    "notes_missing_link": {"attention": 1, "broken": 50},
    # a value outside a closed set breaks every Base that filters on it
    "enum_violations": {"attention": 1, "broken": 20},
    # a required field is what the guideline says the note cannot do without
    "missing_required_fields": {"attention": 1, "broken": 20},
    # a field GL-1002 does not declare is invisible to every live view
    "invented_fields": {"attention": 1, "broken": 20},
    # orphans accumulate slowly; a hundred of them is a graph nobody walks
    "orphans": {"attention": 1, "broken": 100},
    # a link to nothing is a promise the vault does not keep
    "dangling_links": {"attention": 1, "broken": 50},
    # a document whose file is gone is the one failure that loses data
    "documents_without_file": {"attention": 1, "broken": 10},
    # two unprocessed scratchpads is a normal week; fourteen is a backlog
    "unprocessed_scratchpads": {"attention": 2, "broken": 14},
    # the oldest one matters more than the count: age is what rots
    "unprocessed_scratchpad_oldest_days": {"attention": 2, "broken": 14},
    # the inbox is a queue that empties; anything sitting in it is waiting
    "unprocessed_captures": {"attention": 1, "broken": 30},
    # a capture older than three days has stopped being a capture
    "unprocessed_capture_oldest_days": {"attention": 3, "broken": 14},
    # unread references are allowed to wait; a pile of them is a decision
    "unconsumed_references": {"attention": 1, "broken": 30},
    # one thing, one note: a duplicate pair splits a subject in half
    "duplicate_entities": {"attention": 1, "broken": 5},
}

# The metric order IS the contract with the plugin; never reorder.
METRIC_ORDER = [
    ("notes_missing_link", "Notes without a link", "notes"),
    ("enum_violations", "Enum violations", "fields"),
    ("missing_required_fields", "Missing required fields", "notes"),
    ("invented_fields", "Invented fields", "fields"),
    ("orphans", "Orphans", "notes"),
    ("dangling_links", "Dangling links", "links"),
    ("documents_without_file", "Documents without a file", "notes"),
    ("unprocessed_scratchpads", "Unprocessed scratchpads", "notes"),
    ("unprocessed_scratchpad_oldest_days", "Oldest unprocessed scratchpad", "days"),
    ("unprocessed_captures", "Unprocessed captures", "notes"),
    ("unprocessed_capture_oldest_days", "Oldest unprocessed capture", "days"),
    ("unconsumed_references", "Unconsumed references", "notes"),
    ("duplicate_entities", "Duplicate entities", "pairs"),
]
SOP = "SOP-1014"
MAX_FINDINGS = 200
# Two metrics describe one queue: how many are waiting, and how long the
# oldest has waited. A per-file finding belongs to the count metric but
# must carry the worse of the two, or a single scratchpad rotting for a
# month would be filed as `ok` and never shown.
PAIRED = {
    "unprocessed_scratchpads": "unprocessed_scratchpad_oldest_days",
    "unprocessed_captures": "unprocessed_capture_oldest_days",
}

SCAN_ROOTS = ["04 Inner World", "00 Daily Scratchpad", "01 Inbox"]

# Which link fields carry the link rule, per type. GL-1002 states the rule
# in prose ("at least one of projects / key_elements / topics", "no project
# without a goal"), which no table column can hold, so the two rules are
# named here and nowhere else.
LINK_RULE = {
    "note": ("projects", "key_elements", "topics"),
    "project": ("goal",),
}
# Where each entity type lives, for the counts and the duplicate check.
ENTITY_FOLDERS = {
    "person": "04 Inner World/Contacts/People",
    "company": "04 Inner World/Contacts/Companies",
    "project": "04 Inner World/My Life/Projects",
    "goal": "04 Inner World/My Life/Goals",
    "habit": "04 Inner World/My Life/Habits",
    "topic": "04 Inner World/My Life/Topics",
    "key-element": "04 Inner World/My Life/Key Elements",
    "note": "04 Inner World/Notes",
    "document": "04 Inner World/Notes",
}
SKIP_NAMES = {"README.md", "_template.md"}
WIKILINK = re.compile(r"!?\[\[([^\]\n]+)\]\]")
# The captured group is everything between the brackets, escaped alias pipe
# included; `link_name` below is what turns it into a target.
# A fenced block and an inline code span are code, not prose. `[[Some Note]]`
# written inside a fence in an SOP is an EXAMPLE of a link, not a link, and
# counting it made every guideline that teaches wikilinks look like a note
# full of dangling links (Brian Carroll, T16-7). Same reader shape as
# GL-1011's linker, so the two agree on what a code span is. An unterminated
# fence runs to the end of the file, because that is how a renderer reads it.
CODE_FENCE = re.compile(r"(?ms)^[ \t]*(`{3,}|~{3,})[^\n]*\n.*?(?:^[ \t]*\1[^\n]*$|\Z)")
CODE_SPAN = re.compile(r"`[^`\n]*`")
SEVERITY_RANK = {"broken": 0, "attention": 1, "ok": 2}


# --- reading ---------------------------------------------------------------

def blank_code(text):
    """The note with every fenced block and inline code span replaced by
    spaces. BLANKED, not deleted: every offset and every line number stays
    exactly where it was, so a finding still points at the right line."""
    def wipe(m):
        return "".join(c if c == "\n" else " " for c in m.group(0))
    return CODE_SPAN.sub(wipe, CODE_FENCE.sub(wipe, text))


def split_front(text):
    """(frontmatter text, body). Both may be empty; never raises."""
    if not text.startswith("---\n"):
        return "", text
    end = text.find("\n---\n", 4)
    if end == -1:
        return "", text
    return text[4:end], text[end + 5:]


def strip_comment(rest):
    """A frontmatter value without its trailing `# comment`, by the YAML rule:
    a `#` starts a comment after whitespace and outside a quoted scalar. A quote
    only opens one at the start of a value, so the apostrophe in `it's # x`
    opens nothing."""
    quote, opens, i = None, True, 0
    while i < len(rest):
        ch = rest[i]
        if quote == '"' and ch == "\\":
            i += 1
        elif quote == "'" and rest[i:i + 2] == "''":
            i += 1
        elif quote:
            quote = None if ch == quote else quote
        elif ch in "\"'" and opens:
            quote = ch
        elif ch == "#" and i and rest[i - 1].isspace():
            return rest[:i]
        opens = ch in "[," or (ch.isspace() and opens)
        i += 1
    return rest


# A quoted string in the frontmatter. A wikilink is only a link there when it
# is one: `rects: [[72.5, 400, 300, 520]]` on a PDF highlight is numbers, and
# an unquoted `[[X]]` is a list in YAML and no link in Obsidian.
QUOTED = re.compile(r'"(?:[^"\\\n]|\\.)*"|\'(?:[^\'\n]|\'\')*\'')


def front_links(front):
    """Everything in a frontmatter block a link scan may read."""
    return "\n".join(s for line in front.splitlines()
                     for s in QUOTED.findall(strip_comment(line)))


def parse_front(front):
    """{key: value} for a frontmatter block, values kept as written.

    A list is returned as a Python list, a scalar as a string. This is not
    a YAML library and does not need to be: the vault's frontmatter is
    flat, and stdlib-only keeps the script runnable in any vault with no
    install step."""
    out = {}
    lines = front.splitlines()
    i = 0
    while i < len(lines):
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):(.*)$", lines[i])
        if not m:
            i += 1
            continue
        key, rest = m.group(1), strip_comment(m.group(2)).strip()
        if rest.startswith("[") and rest.endswith("]"):
            out[key] = [unquote(v) for v in split_items(rest[1:-1]) if v.strip()]
        elif rest:
            out[key] = unquote(rest)
        else:
            items, j = [], i + 1
            while j < len(lines) and re.match(r"^\s+-\s*", lines[j]):
                items.append(unquote(strip_comment(re.sub(r"^\s+-", "", lines[j]))))
                j += 1
            out[key] = items if items else ""
            i = j - 1
        i += 1
    return out


def split_items(s):
    """Split an inline list on commas that are not inside brackets or quotes."""
    parts, cur, depth, quote = [], [], 0, None
    for ch in s:
        if quote:
            if ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
        elif ch in "[":
            depth += 1
        elif ch in "]":
            depth -= 1
        elif ch == "," and depth == 0:
            parts.append("".join(cur)); cur = []; continue
        cur.append(ch)
    parts.append("".join(cur))
    return parts


def unquote(v):
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        v = v[1:-1]
    return v.strip()


def as_list(value):
    if isinstance(value, list):
        return [v for v in value if str(v).strip()]
    return [value] if str(value).strip() else []


def link_name(raw):
    """The note a wikilink points at: no alias, no heading, no block id."""
    s = str(raw).strip()
    m = re.fullmatch(r"!?\[\[(.+?)\]\]", s)
    if m:
        s = m.group(1)
    # `\|` is the alias separator too. Inside a markdown table a raw pipe
    # ends the cell, so a table link MUST escape it, and Obsidian renders
    # `[[Note\|Alias]]` exactly like `[[Note|Alias]]`. Splitting on the bare
    # pipe alone left the backslash glued to the target and made all 17 table
    # links in SOPs/INDEX.md read as pointing at notes that do not exist
    # (Steven Koegler, 2026-09-01, the same reader defect he reported against
    # the old myPKA validator). A genuinely missing target still dangles: this
    # changes what the target IS, never whether it has to resolve.
    s = re.split(r"\\?\|", s, maxsplit=1)[0]
    # maxsplit= by name: the positional third argument to re.split is
    # deprecated since Python 3.13 and prints a DeprecationWarning straight
    # into the member's terminal (Andrew Gillley, T13-5).
    s = re.split(r"[#^]", s, maxsplit=1)[0]
    return s.strip()


def norm(s):
    return re.sub(r"\s+", " ", str(s).strip()).casefold()


def truthy(v):
    return str(v).strip().strip("\"'").lower() in ("true", "yes", "1")


# --- the run ---------------------------------------------------------------

def hidden(rel):
    return any(p.startswith(".") for p in rel.parts)


def collect(root):
    """Every file in the vault, and every markdown note read once."""
    files, notes = [], {}
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(root)
        if hidden(rel):
            continue
        files.append(rel)
        if p.suffix == ".md":
            text = p.read_text(encoding="utf-8", errors="ignore")
            front, body = split_front(text)
            # `text` is what the note says; `prose` is the same note with code
            # blanked, and is what the link scans read. Of the frontmatter it
            # keeps the quoted strings: a wikilink in a `topics:` list is a
            # real link, a numeric `rects:` array is not.
            notes[rel] = {"front": parse_front(front), "text": text,
                          "body": body, "prose": front_links(front) + "\n" + blank_code(body)}
    return files, notes


def _in_scan(rel):
    """True while this path lives in a room this report reads."""
    return bool(rel.parts) and rel.parts[0] in SCAN_ROOTS


def _is_journal(rel):
    """`06 AI Team/Agents/<Name>/Journal/<entry>.md`, and nothing else.

    An agent journal is written prose with frontmatter and a GL-1002 type,
    and nothing was checking it: SCAN_ROOTS names three rooms and
    `06 AI Team` is not one of them, so a journal entry could carry any
    type at all and this report said ok (Brian Carroll, B2-8).

    The GLOB is in scope, never the room. `06 AI Team` whole is 98 findings
    on the pristine tree and a broken health line, from three separate
    questions nobody has ruled on yet; widening to the room to reach the
    journals would import all of them."""
    p = rel.parts
    return (len(p) == 5 and p[0] == "06 AI Team" and p[1] == "Agents"
            and p[3] == "Journal" and rel.suffix == ".md")


def _shorter(a, b):
    """Obsidian's "shortest path when possible": of two notes that answer to
    the same name, the one nearer the top of the vault wins, and a tie is
    broken on the path string so the answer never depends on walk order.

    With one rule in front of depth (Brian Carroll, B2-3): a candidate
    inside SCAN_ROOTS beats one outside it. A habit and its planner-habit
    note carry the SAME name by design, one in `02 Planner/Habits/` (three
    segments) and one in `04 Inner World/My Life/Habits/` (four). Depth
    alone therefore always picked the Planner copy, every bare `[[X]]` in
    the vault credited its backlink to a note this report does not read,
    and the member's own habit note was reported as an orphan while a link
    to it sat in plain sight. Path-qualified FIELDS fix the fields; they
    cannot fix a bare link written in prose, which is what was reported.

    This is not a departure from Obsidian's rule so much as a reading of
    it: of two notes that answer to the same name, this report prefers the
    one it is actually reporting on."""
    if a is None:
        return b
    return min((a, b), key=lambda r: (not _in_scan(r), len(r.parts),
                                      len(r.as_posix()), r.as_posix()))


def resolver(files, notes=None):
    """Obsidian-shaped link resolution: full path, filename, stem, alias.

    Two corrections over the 1.23.1 reader (Brian Carroll, T16-6). It took
    the FIRST file the walk happened to hand it, so `[[Notes]]` resolved to
    whichever `Notes.md` os.walk reached first and the answer changed with
    the folder name beside it. And it never read `aliases`, so every link
    written to an alias, which is what an alias is for, was reported as
    dangling. Aliases are indexed last and never displace a real filename:
    a note IS its name first.
    """
    by_path, by_name, by_stem, by_alias = {}, {}, {}, {}
    for rel in files:
        for key in (norm(rel.as_posix()), norm(rel.with_suffix("").as_posix())):
            by_path[key] = _shorter(by_path.get(key), rel)
        by_name[norm(rel.name)] = _shorter(by_name.get(norm(rel.name)), rel)
        by_stem[norm(rel.stem)] = _shorter(by_stem.get(norm(rel.stem)), rel)
    for rel, n in (notes or {}).items():
        for al in as_list(n["front"].get("aliases", "")):
            key = norm(link_name(al))
            if key:
                by_alias[key] = _shorter(by_alias.get(key), rel)

    def resolve(name):
        k = norm(name)
        if not k:
            return None
        return (by_path.get(k) or by_name.get(k) or by_stem.get(k)
                or by_alias.get(k))
    return resolve


def note_type(rel, front, known=None):
    """The type of a note: what it declares, else what its room implies.
    A blank daily note declares nothing by design (GL-1007), and a capture
    dropped in the inbox by hand may declare nothing either.

    A declared type that is NOT a GL-1002 type is not a type, so the room
    wins over it. Before 2026-09-14 a declared value won unconditionally, and
    a scratchpad carrying `type: daily` left the unprocessed queue with
    `processed: false` still on it while the report said zero of everything
    (pilot A finding F8). The value is not swallowed: the caller reports it
    as an enum violation naming what the allowed values are."""
    t = str(front.get("type", "")).strip()
    if t and (known is None or t in known):
        return t
    first = rel.parts[0] if rel.parts else ""
    if first == "00 Daily Scratchpad":
        return "scratchpad"
    if first == "01 Inbox":
        return "capture"
    return ""


def age_days(rel, root, front, today):
    """How long this has been waiting: the date it carries, else its mtime."""
    for key in ("date", "captured", "created"):
        v = str(front.get(key, ""))[:10]
        try:
            return (today - datetime.date.fromisoformat(v)).days
        except ValueError:
            pass
    m = re.match(r"(\d{4}-\d{2}-\d{2})", rel.stem)
    if m:
        try:
            return (today - datetime.date.fromisoformat(m.group(1))).days
        except ValueError:
            pass
    ts = (root / rel).stat().st_mtime
    return (today - datetime.date.fromtimestamp(ts)).days


def run(root):
    today = datetime.date.today()
    declared = new_base.gl002_fields(root)
    required = new_base.gl002_required(root)
    enums = new_base.gl002_enums(root)
    # The type column of the same table. A value outside it is not a type,
    # and nothing downstream may act on it as if it were.
    known_types = set(declared) | {"scratchpad", "capture"}
    # Which guideline a type's fields live in: GL-1015 for the team half,
    # GL-1002 for everything else. Named in the finding so the fix lands in
    # the right file.
    team = new_base.team_types(root)

    def gl(t):
        return "GL-1015" if t in team else "GL-1002"

    files, notes = collect(root)
    resolve = resolver(files, notes)
    findings = []
    values = {k: 0 for k, _, _ in METRIC_ORDER}

    def add(metric, path, message, action):
        findings.append({"metric": metric, "severity": None,
                         "path": path, "message": message, "action": action})

    # Backlinks over the WHOLE vault: a link from a Workstream or a Planner
    # note counts. A note that links to itself is not linked to.
    linked_to = set()
    for rel, n in notes.items():
        for raw in WIKILINK.findall(n["prose"]):
            tgt = resolve(link_name(raw))
            if tgt is not None and tgt != rel:
                linked_to.add(tgt)

    in_scan = [rel for rel in notes
               if (_in_scan(rel) or _is_journal(rel))
               and rel.name not in SKIP_NAMES]

    scratchpad_ages, capture_ages = [], []
    identities = {}          # (folder, normalised name) -> [paths]

    for rel in sorted(in_scan):
        n = notes[rel]
        front = n["front"]
        t = note_type(rel, front, known_types)
        posix = rel.as_posix()

        # --- the type itself is an enum ------------------------------------
        declared_type = str(front.get("type", "")).strip()
        if declared_type and declared_type not in known_types:
            values["enum_violations"] += 1
            add("enum_violations", posix,
                "`type` is `%s`, which is not one of the types GL-1002 or GL-1015 declares."
                % declared_type,
                "Set `type` to one of %s." % ", ".join(sorted(known_types)))
        archived = "/archive/" in "/" + posix

        # --- the link rule -------------------------------------------------
        if t in LINK_RULE:
            if not any(as_list(front.get(f, "")) for f in LINK_RULE[t]):
                values["notes_missing_link"] += 1
                add("notes_missing_link", posix,
                    "The note links to nothing in the vault.",
                    "Add one wikilink in %s to the thing it belongs to."
                    % " / ".join(LINK_RULE[t]))

        # --- enums ---------------------------------------------------------
        for field, allowed in enums.get(t, {}).items():
            v = str(front.get(field, "")).strip()
            if v and v not in allowed:
                values["enum_violations"] += 1
                add("enum_violations", posix,
                    "`%s` is `%s`, which is not one of %s."
                    % (field, v, ", ".join(allowed)),
                    "Set `%s` to one of %s." % (field, ", ".join(allowed)))

        # --- required fields ------------------------------------------------
        # A scratchpad is exempt: GL-1007 ships the daily note blank on
        # purpose, and frontmatter appears on it only when it is stamped.
        if t and t != "scratchpad" and t in required and front:
            for field in sorted(required[t]):
                if not as_list(front.get(field, "")):
                    values["missing_required_fields"] += 1
                    add("missing_required_fields", posix,
                        "Required field `%s` is missing or empty." % field,
                        "Fill `%s` in the Properties panel (%s)." % (field, gl(t)))

        # --- invented fields -------------------------------------------------
        if t in declared:
            for field in sorted(front):
                if field not in declared[t]:
                    values["invented_fields"] += 1
                    add("invented_fields", posix,
                        "`%s` is not a %s field for type `%s`." % (field, gl(t), t),
                        "Rename it to the %s field that means this, or "
                        "add it to %s first and then use it." % (gl(t), gl(t)))

        # --- dangling links ---------------------------------------------------
        for raw in WIKILINK.findall(n["prose"]):
            name = link_name(raw)
            if not name:
                continue      # [[#heading]]: a link inside this note
            if resolve(name) is None:
                values["dangling_links"] += 1
                add("dangling_links", posix,
                    "`[[%s]]` points at a note that does not exist." % name,
                    "Point it at the note that exists, or create `%s`." % name)

        # --- documents without their file --------------------------------------
        if t == "document":
            sf = as_list(front.get("source_file", ""))
            if not sf:
                values["documents_without_file"] += 1
                add("documents_without_file", posix,
                    "A document wrapper note with no `source_file`.",
                    "Link the file in 05 Assets/Documents with `source_file`.")
            elif resolve(link_name(sf[0])) is None:
                values["documents_without_file"] += 1
                add("documents_without_file", posix,
                    "`source_file` points at `%s`, which is not in the vault."
                    % link_name(sf[0]),
                    "Move the file onto the shelf in 05 Assets/Documents, "
                    "or fix the link.")

        # --- the queues ---------------------------------------------------------
        # A blank scratchpad is not a queue item. link-dates-to-daily-notes.py
        # --fix CREATES the daily note for any day a link points at, empty and
        # on purpose (GL-1007), so a member who linked forty dates woke up to
        # forty "unprocessed scratchpads" and an oldest-unprocessed age
        # measured from a note nobody had written in (Brian Carroll, T16-5).
        # Nothing to process means nothing to report, and it stays out of the
        # oldest-unprocessed clock too.
        if t == "scratchpad" and n["body"].strip() \
                and not truthy(front.get("processed", "")):
            days = age_days(rel, root, front, today)
            scratchpad_ages.append(days)
            values["unprocessed_scratchpads"] += 1
            add("unprocessed_scratchpads", posix,
                "Scratchpad is %d day(s) old and not processed." % days,
                "Process it (SOP-1001), or stamp it by hand if you already "
                "carried it into its homes.")

        # --- unconsumed references ------------------------------------------------
        if t == "note" and str(front.get("note_type", "")).strip() == "reference" \
                and not truthy(front.get("consumed", "")):
            values["unconsumed_references"] += 1
            add("unconsumed_references", posix,
                "A reference you have not read or watched yet.",
                "Read it and tick `consumed`, or let it wait; the Topic page "
                "lists it either way.")

        # --- duplicates ------------------------------------------------------------
        folder = rel.parent.as_posix()
        if folder in ENTITY_FOLDERS.values() and not archived:
            keys = {norm(rel.stem)}
            for field in ("name", "title"):
                if front.get(field):
                    keys.add(norm(front[field]))
            for al in as_list(front.get("aliases", "")):
                keys.add(norm(al))
            for k in keys:
                identities.setdefault((folder, t, k), []).append(posix)

    # --- the inbox queue: markdown captures AND binaries still waiting ---------
    inbox = root / "01 Inbox"
    inbox_files = []
    if inbox.is_dir():
        for p in sorted(inbox.rglob("*")):
            rel = p.relative_to(root)
            if not p.is_file() or hidden(rel) or p.name in SKIP_NAMES \
                    or p.name == ".gitkeep" or "archive" in rel.parts:
                continue
            inbox_files.append(rel)
            front = notes.get(rel, {}).get("front", {})
            if truthy(front.get("processed", "")):
                continue
            days = age_days(rel, root, front, today)
            capture_ages.append(days)
            values["unprocessed_captures"] += 1
            add("unprocessed_captures", rel.as_posix(),
                "Capture has sat in the inbox for %d day(s)." % days,
                "File it into the room it belongs to (SOP-1002); the original "
                "is archived, never deleted.")

    values["unprocessed_scratchpad_oldest_days"] = max(scratchpad_ages or [0])
    values["unprocessed_capture_oldest_days"] = max(capture_ages or [0])

    for (folder, _t, key), paths in sorted(identities.items()):
        uniq = sorted(set(paths))
        if len(uniq) > 1:
            values["duplicate_entities"] += 1
            add("duplicate_entities", uniq[0],
                "`%s` names the same thing as %s." % (key, ", ".join(uniq[1:])),
                "Decide which note stays, fold the other one's facts into it, "
                "and remove the one that goes.")

    # --- orphans: nothing in the vault links here -------------------------------
    # Only things that are MEANT to be linked to: entities and Notes. A
    # journal entry nobody links to is a normal journal entry. `example`
    # notes are excluded: the scaffold ships them unlinked on purpose.
    orphan_folders = set(ENTITY_FOLDERS.values())
    for rel in sorted(in_scan):
        if rel.parent.as_posix() not in orphan_folders:
            continue
        front = notes[rel]["front"]
        if "example" in [norm(t) for t in as_list(front.get("tags", ""))]:
            continue
        if rel in linked_to:
            continue
        values["orphans"] += 1
        add("orphans", rel.as_posix(),
            "Nothing in the vault links to this note.",
            "Link it from the Project, Key Element or Topic it belongs to, "
            "or merge it into a note that exists.")

    # --- counts ------------------------------------------------------------------
    def count_folder(folder, typ=None):
        """How many notes of a kind a room holds. Recursive on purpose: a
        count that stopped at the top level would disagree with the metrics
        above, which walk the whole room, and a member who made one subfolder
        would be told the two numbers by two different rules."""
        d = root / folder
        if not d.is_dir():
            return 0
        n = 0
        for p in d.rglob("*.md"):
            rel = p.relative_to(root)
            if p.name in SKIP_NAMES or hidden(rel) or "archive" in rel.parts:
                continue
            if typ is not None:
                if note_type(rel, notes.get(rel, {}).get("front", {}),
                             known_types) != typ:
                    continue
            n += 1
        return n

    journal_dir = root / "04 Inner World/Journal"
    counts = {
        "journal": sum(1 for p in journal_dir.rglob("*.md")
                       if p.name not in SKIP_NAMES) if journal_dir.is_dir() else 0,
        "notes": count_folder("04 Inner World/Notes", "note"),
        "documents": count_folder("04 Inner World/Notes", "document"),
        "people": count_folder(ENTITY_FOLDERS["person"]),
        "companies": count_folder(ENTITY_FOLDERS["company"]),
        "projects": count_folder(ENTITY_FOLDERS["project"]),
        "goals": count_folder(ENTITY_FOLDERS["goal"]),
        "habits": count_folder(ENTITY_FOLDERS["habit"]),
        "topics": count_folder(ENTITY_FOLDERS["topic"]),
        "key_elements": count_folder(ENTITY_FOLDERS["key-element"]),
        "scratchpads": count_folder("00 Daily Scratchpad"),
        "inbox": len(inbox_files),
    }

    # --- severities -----------------------------------------------------------------
    def severity(mid, value):
        th = THRESHOLDS[mid]
        if value >= th["broken"]:
            return "broken"
        if value >= th["attention"]:
            return "attention"
        return "ok"

    metrics = []
    by_metric = {}
    for mid, label, unit in METRIC_ORDER:
        sev = severity(mid, values[mid])
        by_metric[mid] = sev
        metrics.append({"id": mid, "label": label, "value": values[mid],
                        "unit": unit, "severity": sev,
                        "threshold": THRESHOLDS[mid], "sop": SOP})
    # A finding carries its metric's severity (the worse of a paired queue),
    # and a finding under a metric that is still `ok` is dropped: it is true
    # but there is nothing to act on yet, and the report is a to-do list.
    kept = []
    for f in findings:
        sev = by_metric.get(f["metric"], "attention")
        pair = PAIRED.get(f["metric"])
        if pair and SEVERITY_RANK[by_metric[pair]] < SEVERITY_RANK[sev]:
            sev = by_metric[pair]
        if sev == "ok":
            continue
        f["severity"] = sev
        kept.append(f)
    findings = kept
    findings.sort(key=lambda f: (SEVERITY_RANK[f["severity"]], f["metric"], f["path"]))
    health = "ok"
    for m in metrics:
        if m["severity"] == "broken":
            health = "broken"
            break
        if m["severity"] == "attention":
            health = "attention"

    version = "unknown"
    vf = root / ".icor-for-life/VERSION"
    if vf.is_file():
        version = vf.read_text(encoding="utf-8").strip() or "unknown"

    return {
        "schema": SCHEMA,
        "generated": datetime.datetime.now(datetime.timezone.utc)
                     .strftime("%Y-%m-%dT%H:%M:%SZ"),
        "scaffold_version": version,
        "health": health,
        "counts": counts,
        "metrics": metrics,
        "findings": findings[:MAX_FINDINGS],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default=None)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    root = Path(a.root).resolve() if a.root else DEFAULT_ROOT
    if not root.is_dir():
        sys.exit("FAIL no such folder: %s" % root)
    if not (root / "04 Inner World").is_dir():
        sys.exit("FAIL %s is not a scaffold root (no '04 Inner World'); "
                 "give the vault root" % root)

    started = time.time()
    report = run(root)
    elapsed = time.time() - started

    if a.write:
        dest = root / ".icor-for-life/scripts/quality.json"
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        except OSError as exc:
            sys.exit("FAIL cannot write %s: %s" % (dest, exc))
        if not a.json:
            print("OK wrote %s" % dest.relative_to(root))

    if a.json:
        print(json.dumps(report, indent=2))
        return 0

    total = len(report["findings"])
    print("health: %s   (%s, %.1fs)"
          % (report["health"], report["scaffold_version"], elapsed))
    print("counts: " + ", ".join("%s %d" % (k, v)
                                 for k, v in report["counts"].items()))
    print()
    for m in report["metrics"]:
        print("%-8s %-34s %5d %s" % (m["severity"], m["label"], m["value"], m["unit"]))
    if total:
        print("\nfindings (%d shown, worst first):" % total)
        for f in report["findings"]:
            print("  [%s] %s" % (f["severity"], f["path"]))
            print("      %s" % f["message"])
            print("      -> %s" % f["action"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
