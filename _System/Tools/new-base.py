#!/usr/bin/env python3
"""Stamp a house-shaped Obsidian .base file for one entity collection.

Usage:
  new-base.py <entity>            entity: person | company | document | note
                                  | goal | project | key-element | topic | habit
  new-base.py --list              show the registry
  new-base.py <entity> --root X   operate on another scaffold root

Per GL-1006: Bases are VIEWS over frontmatter and are generated, never
hand-authored. Guards (code, not prose):
  - refuses an entity type that is not in the registry
  - refuses to overwrite an existing .base
  - refuses a registry column that GL-1002 does not declare (a drifted
    registry must lose to the guideline, never win)
  - refuses when the target folder does not exist

One folder can hold more than one collection when the notes differ by
`type`: 04 Inner World/Notes carries Documents.base (type document, the
file wrappers) and Notes.base (type note). A collection is therefore
(folder, type), and check-bases.py keys its one-Base-per-collection rule
the same way.
"""
import argparse, importlib.util, re, sys
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

# noteio-icor.py sits beside this script and is loaded by path, not by name, so
# the import needs nothing on sys.path, which is what lets this script run
# under the `-I -B -X utf8` the rendered hooks carry, with its own folder
# dropped from sys.path. A missing noteio-icor.py is a half-upgraded Scripts/
# folder and says so in one line, because a traceback out of an import
# teaches the member nothing about what to do next.
_nio_path = Path(__file__).resolve().parent / "noteio-icor.py"
if not _nio_path.is_file():
    raise SystemExit("FAIL noteio-icor.py is missing from %s. Scripts/ is half "
                     "upgraded; restore noteio-icor.py beside this script and run "
                     "this again." % _nio_path.parent)
_nio = importlib.util.spec_from_file_location("noteio", _nio_path)
noteio = importlib.util.module_from_spec(_nio)
_nio.loader.exec_module(noteio)

DEFAULT_ROOT = Path(__file__).resolve().parents[2]
GL002 = "06 AI Team/AI Team Knowledge/Guidelines/GL-1002-frontmatter-conventions.md"
# The team half of the per-type table (split step 10, 2026-09-24): task,
# session-log, sop / workstream / guideline, journal-entry, agent and the
# other `side: team` types of icor-concepts/1 live in myPKA's GL-1015, not in
# GL-1002. GL-1002 is always read and must exist; GL-1015 is read when it is
# under the same root, which is mode A (myPKA unpacked into this folder) and a
# staged merge. A bare ICOR for Life folder (mode B, or no team at all) holds
# no team notes, so its table is the content half alone and nothing is lost.
GL015 = "06 AI Team/AI Team Knowledge/Guidelines/GL-1015-team-frontmatter-conventions.md"


def _guideline_texts(root):
    """The texts the per-type table is read from: GL-1002, then GL-1015 when
    present. Both tables share one header shape, so one parser reads both and
    no field list is copied anywhere (GL-1005)."""
    texts = [(root / GL002).read_text(encoding="utf-8")]
    team = root / GL015
    if team.is_file():
        texts.append(team.read_text(encoding="utf-8"))
    return texts

# The registry: which collections earn a Base, and their canonical
# table shape. Columns are GL-1002 note properties; file.name is always
# the identity column and is added by render(), not listed here.
REGISTRY = {
    "person": {
        "folder": "04 Inner World/Contacts/People",
        "base": "People.base",
        "view": "People",
        "type_value": "person",
        "columns": [
            ("role", "Role"),
            ("relation", "Relation"),
            ("companies", "Companies"),
            ("email", "Email"),
            ("last_contact", "Last contact"),
            ("next_action", "Next action"),
        ],
        "sort": ("file.name", "ASC"),
        "cards_image": None,
        "extra_views": [],
    },
    "company": {
        "folder": "04 Inner World/Contacts/Companies",
        "base": "Companies.base",
        "view": "Companies",
        "type_value": "company",
        "columns": [
            ("industry", "Industry"),
            ("people", "People"),
            ("website", "Website"),
        ],
        "sort": ("file.name", "ASC"),
        "cards_image": None,
    },
    "document": {
        "folder": "04 Inner World/Notes",
        "base": "Documents.base",
        "view": "Documents",
        "type_value": "document",
        "columns": [
            ("doc_type", "Kind"),
            ("issued_on", "Issued"),
            ("expiry_date", "Expires"),
            ("amount", "Amount"),
            ("currency", "Currency"),
            ("source_file", "File"),
        ],
        "sort": ("note.issued_on", "DESC"),
        "cards_image": "note.preview_image",
    },
    # The five My Life rooms. Promoted from GL-1006's "later candidates" on
    # 2026-09-15: these are the rooms that answer "what are my goals",
    # "which projects am I focused on" and "what are my key elements", and
    # they are edited as rows, which is exactly the decision test.
    "goal": {
        "folder": "04 Inner World/My Life/Goals",
        "base": "Goals.base",
        "view": "Goals",
        "type_value": "goal",
        "columns": [
            ("status", "Status"),
            ("target_date", "Target"),
            ("key_elements", "Key Elements"),
        ],
        "sort": ("file.name", "ASC"),
        "cards_image": None,
        "extra_views": [
            # The answer to "what are my goals". Open goals only, soonest
            # target first, so the list is ordered by when rather than by
            # name: a goal two months past its target has to be visible
            # without anybody sorting the table by hand.
            {"name": "Active", "filters": ['note.status == "not-achieved"'],
             "order": ["target_date", "key_elements"],
             "sort": ("note.target_date", "ASC")},
        ],
    },
    "project": {
        "folder": "04 Inner World/My Life/Projects",
        "base": "Projects.base",
        "view": "Projects",
        "type_value": "project",
        "columns": [
            # Focus first: `focus_rank` is your decision about what matters
            # now (1, 2 or 3, absent means not in focus), and a decision
            # belongs in the leftmost column, not buried at the right.
            ("focus_rank", "Focus"),
            ("status", "Status"),
            ("goal", "Goal"),
            ("start_date", "Started"),
            ("end_date", "Ended"),
            ("key_elements", "Key Elements"),
        ],
        "sort": ("file.name", "ASC"),
        "cards_image": None,
        "extra_views": [
            # The answer to "which projects should I focus on". Open work
            # only, your ranks at the top. Obsidian sorts an empty property
            # last, which is what makes the unranked projects fall below
            # the three you chose without a second filter.
            {"name": "Active", "filters": ['note.status == "active"'],
             "order": ["focus_rank", "goal", "start_date", "key_elements"],
             "sort": ("note.focus_rank", "ASC")},
        ],
    },
    "key-element": {
        "folder": "04 Inner World/My Life/Key Elements",
        "base": "Key Elements.base",
        "view": "Key Elements",
        "type_value": "key-element",
        "columns": [
            ("goals", "Goals"),
            ("people", "People"),
        ],
        "sort": ("file.name", "ASC"),
        "cards_image": None,
    },
    "topic": {
        "folder": "04 Inner World/My Life/Topics",
        "base": "Topics.base",
        "view": "Topics",
        "type_value": "topic",
        "columns": [
            ("related_topics", "Related"),
        ],
        "sort": ("file.name", "ASC"),
        "cards_image": None,
    },
    "habit": {
        "folder": "04 Inner World/My Life/Habits",
        "base": "Habits.base",
        "view": "Habits",
        "type_value": "habit",
        "columns": [
            ("status", "Status"),
            # The link to the Planner note that carries the cadence and the
            # log. The meaning lives here, the tracking lives there, and
            # this column is the one place you can see which is which.
            ("planner_habit", "Planner"),
        ],
        "sort": ("file.name", "ASC"),
        "cards_image": None,
    },
    "note": {
        "folder": "04 Inner World/Notes",
        "base": "Notes.base",
        "view": "Notes",
        "type_value": "note",
        "columns": [
            ("note_type", "Kind"),
            ("projects", "Projects"),
            ("key_elements", "Key Elements"),
            ("topics", "Topics"),
            ("source_url", "Source"),
            ("consumed", "Consumed"),
        ],
        "sort": ("file.name", "ASC"),
        "cards_image": None,
        "extra_views": [
            # The outer-world library. GL-1007: outer material does not live
            # in a room of its own; once it carries your thought it is part of
            # what you know, and the source is recorded in a property. This
            # view is that library.
            {"name": "Sources", "filters": ['note.note_type == "reference"'],
             "order": ["source_url", "consumed", "topics", "key_elements"],
             "sort": ("note.consumed", "ASC")},
            # The reading queue. Unconsumed sources only, so the list supports
            # action when you turn to the subject instead of nagging. `!= true`
            # and not `== false`: in Bases a missing property is not equal to
            # false, so a reference with no `consumed` field fell out of the
            # queue while check-quality.py counted it as unread (member report
            # on 2.2.1, item 3). Both now say: unread unless it is `true`.
            {"name": "Reading queue", "filters": ['note.note_type == "reference"', "note.consumed != true"],
             "order": ["source_url", "topics", "key_elements"],
             "sort": ("file.name", "ASC")},
            # Ideas you have not decided on yet. An idea with no status is
            # open; one that is promoted, parked or dropped leaves this list.
            {"name": "Open ideas", "filters": ['note.note_type == "idea"', 'note.idea_status == "open"'],
             "order": ["key_elements", "projects", "topics"],
             "sort": ("file.name", "ASC")},
        ],
    },
}

# Fields every note carries per GL-1002's common block.
COMMON_FIELDS = {"type", "created", "tags"}


# The two columns of GL-1002's per-type table that hold field names. The
# table also carries a `template` column (added 2026-09-09) and may carry
# more later; columns are found BY HEADER NAME, never by position, so a
# new column can never shift the parse. It did once: with positional
# `(.+)|(.+)` the required and optional cells were read as ONE cell joined
# by a pipe, which silently ate the first field of the optional column and
# failed all four shipped bases.
FIELD_COLUMNS = ("required fields", "optional fields")
TYPE_COLUMN = "type"


def _table_row(line):
    """The cells of a markdown table row, or None when the line is not one."""
    s = line.strip()
    if not (s.startswith("|") and s.endswith("|")):
        return None
    return [c.strip() for c in s[1:-1].split("|")]


def _gl002_table(root, columns, texts=None):
    """Read the per-type table (GL-1002, plus GL-1015's team rows when that
    file is under ROOT) and return {type: set(field names)},
    taking the field names from the named COLUMNS only.

    Deterministic, and column-order independent: the header row that names
    both FIELD_COLUMNS opens the table and fixes the column indices by
    name; every row until the table ends is a type. Within a cell,
    parentheticals are stripped (they hold enums and commentary, and may
    contain commas), then the cell splits on commas AND semicolons: a cell
    may carry a rule clause after the field list (`note_type (...); at
    least one of projects / ...`) and a clause is prose, never a field, so
    it drops out of the token filter. Other tables in GL-1002 (the
    pdf-highlight field table, the habit-log markers) never carry both
    header names, so they are skipped.
    """
    text = "\n\n".join(texts if texts is not None else _guideline_texts(root))
    out = {}
    cols = None          # header name -> index, while inside the table
    for line in text.splitlines():
        cells = _table_row(line)
        if cells is None:
            cols = None  # any non-table line ends the table
            continue
        low = [c.lower() for c in cells]
        if all(name in low for name in FIELD_COLUMNS) and TYPE_COLUMN in low:
            cols = {name: low.index(name)
                    for name in (TYPE_COLUMN,) + FIELD_COLUMNS}
            continue
        if cols is None:
            continue
        if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
            continue     # the header separator row
        if max(cols.values()) >= len(cells):
            continue     # a malformed row: never guess at its columns
        tname = cells[cols[TYPE_COLUMN]]
        if not re.fullmatch(r"[a-z-]+(?:\s*/\s*[a-z-]+)*", tname):
            continue
        fields = set()
        for name in columns:
            cell = re.sub(r"\([^)]*\)", "", cells[cols[name]])
            for f in re.split(r"[,;]", cell):
                f = f.strip()
                if re.fullmatch(r"[a-z][a-z0-9_]*", f):
                    fields.add(f)
        for t in re.split(r"\s*/\s*", tname):
            out[t] = fields
    return out


def gl002_fields(root):
    """{type: set(EVERY field The schema declares)}, required and optional
    together plus the common block. This is the "is this field invented"
    answer: a key outside this set for its type is not in the guideline."""
    return {t: f | COMMON_FIELDS
            for t, f in _gl002_table(root, FIELD_COLUMNS).items()}


def team_types(root):
    """The types GL-1015 declares (the team half), empty when GL-1015 is not
    under ROOT. A report names the guideline a type's fields live in, and a
    team field is added to GL-1015 first, never to GL-1002."""
    team = root / GL015
    if not team.is_file():
        return set()
    return set(_gl002_table(root, FIELD_COLUMNS,
                            [team.read_text(encoding="utf-8")]))


def gl002_required(root):
    """{type: set(REQUIRED fields)} from the same table, same reader.

    check-quality.py asks "which fields must this note carry"; the answer
    is the `required fields` column alone, so it cannot be taken from
    gl002_fields (which unions both columns for the "is this field
    invented" question). One parser, two questions, no second copy of the
    table. `type` and `created` are common to every note GL-1002 declares
    and are NOT added here: a required-field report is about what the
    guideline says per type, and the common block is checked once by the
    caller."""
    return _gl002_table(root, ("required fields",))


# A closed value set in GL-1002 is written as `field (a/b/c)` right after
# the field name. That is the ONLY shape read as an enum: every token must
# be a bare lowercase word, so `source_file (wikilink to the binary in
# 05 Assets/Documents, MANDATORY)` (a slash inside prose) and
# `priority (1-5)` (a range) are not enums and are left alone.
ENUM_CELL = re.compile(r"([a-z][a-z0-9_]*)\s*\(([^)]*)\)")


def gl002_enums(root):
    """{type: {field: [allowed values]}} from the same table, same reader.

    The value sets are stated once, in the guideline, beside the field they
    belong to. `status` means different things on a goal, a project and a
    habit, so the map is keyed by type first: a hardcoded copy in a checker
    would have to repeat that distinction and would be wrong the day one of
    them changes."""
    text = "\n\n".join(_guideline_texts(root))
    out = {}
    cols = None
    for line in text.splitlines():
        cells = _table_row(line)
        if cells is None:
            cols = None
            continue
        low = [c.lower() for c in cells]
        if all(name in low for name in FIELD_COLUMNS) and TYPE_COLUMN in low:
            cols = {name: low.index(name)
                    for name in (TYPE_COLUMN,) + FIELD_COLUMNS}
            continue
        if cols is None or max(cols.values()) >= len(cells):
            continue
        tname = cells[cols[TYPE_COLUMN]]
        if not re.fullmatch(r"[a-z-]+(?:\s*/\s*[a-z-]+)*", tname):
            continue
        found = {}
        for name in FIELD_COLUMNS:
            for field, inside in ENUM_CELL.findall(cells[cols[name]]):
                inside = inside.split(";")[0]          # drop a trailing clause
                if "/" not in inside:
                    continue
                values = [v.strip() for v in inside.split("/")]
                if all(re.fullmatch(r"[a-z][a-z0-9-]*", v) for v in values) \
                        and len(values) > 1:
                    found[field] = values
        if found:
            for t in re.split(r"\s*/\s*", tname):
                out.setdefault(t, {}).update(found)
    return out


# --- the per-type table, from _System/schema.json (ICOR for Life without 06 AI Team) ---------------
# The guidelines are gone; the schema holds the same table as data. These four replace the GL-1002 readers
# above, with the same answers, so every script that imports them is unchanged.
SCHEMA = "_System/schema.json"


def _schema(root):
    import json
    return json.loads((Path(root) / SCHEMA).read_text(encoding="utf-8"))


def gl002_fields(root):
    s = _schema(root)
    return {t: set(v["fields"]) | set(s["common"]) for t, v in s["types"].items()}


def gl002_required(root):
    return {t: set(v["required"]) for t, v in _schema(root)["types"].items()}


def gl002_enums(root):
    return {t: dict(v["values"]) for t, v in _schema(root)["types"].items() if v["values"]}


def team_types(root):
    return set()


def render(entity):
    e = REGISTRY[entity]
    L = []
    L.append("# Generated by _System/Tools/new-base.py")
    L.append("# Columns are GL-1002 fields. To change them: update GL-1002,")
    L.append("# then the registry in new-base.py, then re-stamp (GL-1006).")
    L.append("filters:")
    L.append("  and:")
    L.append('    - file.inFolder("%s")' % e["folder"])
    L.append('    - file.ext == "md"')
    L.append('    - note.type == "%s"' % e["type_value"])
    L.append("properties:")
    L.append("  file.name:")
    L.append("    displayName: Name")
    for prop, disp in e["columns"]:
        L.append("  note.%s:" % prop)
        L.append("    displayName: %s" % disp)
    L.append("views:")
    L.append("  - type: table")
    L.append("    name: %s" % e["view"])
    L.append("    order:")
    L.append("      - file.name")
    for prop, _ in e["columns"]:
        L.append("      - note.%s" % prop)
    L.append("    sort:")
    L.append("      - property: %s" % e["sort"][0])
    L.append("        direction: %s" % e["sort"][1])
    # Named views over the SAME collection. A collection is (folder, type)
    # per GL-1006, so a second kind inside one type is a VIEW, never a second
    # Base and never a second folder. This is what makes "the outer world
    # library" a filter rather than a room.
    for v in e.get("extra_views") or []:
        L.append("  - type: table")
        L.append("    name: %s" % v["name"])
        L.append("    filters:")
        L.append("      and:")
        for f in v["filters"]:
            L.append("        - %s" % f)
        L.append("    order:")
        L.append("      - file.name")
        for prop in v["order"]:
            L.append("      - note.%s" % prop)
        L.append("    sort:")
        L.append("      - property: %s" % v["sort"][0])
        L.append("        direction: %s" % v["sort"][1])
    if e["cards_image"]:
        L.append("  - type: cards")
        L.append("    name: %s gallery" % e["view"])
        L.append("    image: %s" % e["cards_image"])
        L.append("    order:")
        L.append("      - file.name")
        for prop, _ in e["columns"][:3]:
            L.append("      - note.%s" % prop)
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("entity", nargs="?")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--root", default=None)
    a = ap.parse_args()
    root = Path(a.root).resolve() if a.root else DEFAULT_ROOT

    if a.list:
        for name, e in REGISTRY.items():
            print("%-10s -> %s/%s" % (name, e["folder"], e["base"]))
        return 0

    if not a.entity:
        sys.exit("FAIL name an entity type (or --list)")
    if a.entity not in REGISTRY:
        sys.exit("FAIL unknown entity type %r; registry knows: %s"
                 % (a.entity, ", ".join(sorted(REGISTRY))))

    e = REGISTRY[a.entity]
    declared = gl002_fields(root).get(e["type_value"], COMMON_FIELDS)
    undeclared = [p for p, _ in e["columns"] if p not in declared]
    if undeclared:
        sys.exit("FAIL registry columns not declared in the schema for %r: %s "
                 "(update the guideline first, per CLAUDE.md hard rule 4)"
                 % (a.entity, ", ".join(undeclared)))

    folder = root / e["folder"]
    if not folder.is_dir():
        sys.exit("FAIL target folder missing: %s" % e["folder"])
    dest = folder / e["base"]
    if dest.exists():
        sys.exit("FAIL %s exists, refusing to overwrite "
                 "(delete it first if a re-stamp is intended)"
                 % dest.relative_to(root))

    noteio.write_note(dest, render(a.entity))
    print("OK stamped -> %s" % dest.relative_to(root))
    return 0


if __name__ == "__main__":
    sys.exit(main())
