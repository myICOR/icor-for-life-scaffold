#!/usr/bin/env python3
"""Validate the ICOR for Life Scaffold structure and naming rules.

Checks (all deterministic, per GL-1001 and GL-1004):
  1. The six rooms and their required subfolders exist.
  2. No folder at any level is named after an ICOR stage.
  3. Daily Scratchpad files sit in YYYY/MM/ and are named YYYY-MM-DD.md
     (daily note), YYYYMMDDHHmm.md (quick capture) or
     YYYY-MM-DD_canvas.canvas.
  4. Journal entries sit in YYYY/MM/ and are named YYYY-MM-DD_<slug>.md.
  5. (moved) Session logs and task nesting: myPKA validate-team.py.
  6. Every folder inside a room resolves a colour and a glyph from the
     file-tree rules of the INKLINE theme (.obsidian/themes/*/theme.css,
     since 1.4.0; the icor-rooms.css snippet before that), so a new
     folder can never ship as bare text in the file tree the way
     "AI Sessions" did (2026-08-30). With NO rule source in the vault the
     check is reported SKIPPED, on stdout and in --json, never as passed.
  7. Every note in 02 Planner/Habits/ has the planner-habit shape (type,
     name, cadence, status, cadence_days/month_day value sets).
  8. Every note in 02 Planner/Routines/ has the planner-routine shape
     (type, routine_type, HH:MM start before end, weekdays, active).
  9. (moved) Agent folders and their myicor_id: myPKA validate-team.py.
 10. Every `type: note` file in 04 Inner World/Notes/ carries a note_type
     from GL-1002's set (reference, idea, outline, meeting, draft, other)
     and at
     least one non-empty link list among projects / key_elements / topics
     (GL-1007: a note that lives on is filed under something).
 11. .obsidian/daily-notes.json carries no `template` key: the daily
     scratchpad stays blank (GL-1007), so no journal properties leak into
     raw capture. Its `format` is the one GL-1004 names,
     YYYY/MM/YYYY-MM-DD: check 3 enforces the nesting, and GL-1011's
     [[YYYY-MM-DD]] links only resolve while the note is named that.
 12. .obsidian/templates.json points at 06 AI Team/AI Team Knowledge/
     Templates, every template there declares a `type` GL-1002 knows, and
     every template GL-1002's per-type table names exists. Without this
     the by-hand path in GL-1007 (Templates: Insert template) has nothing
     behind it.
 13. .obsidian/types.json declares every LIST property as multitext, so a
     wikilink list arrives in the Properties panel as a list of links a
     member can add to with `[[`, not as one string. The list of list
     properties is read from the templates themselves, which GL-1002
     names as the one place the field list is spelled out as YAML.
 16. In the Scaffold SOURCE REPO only, every bucket under 03 WiP/ holds
     nothing but its README.md: the member gets an empty working surface,
     never somebody else's leftover work (Tom, 2026-09-18). In any other
     tree a full 03 WiP/ is the room working as designed, so the check
     reports itself SKIPPED and is never counted as passed.
(15, moved) The root entry contract (AGENTS.md and its adapters): myPKA
     validate-team.py.

CONTENT ONLY (myPKA split, 10-placement row 3). This script checks what the
ICOR for Life folder ships and keeps, and it passes on that folder alone.
Everything the team ships (06 AI Team/Agents, SOPs, Tasks, Session Logs,
Expansions, AI Sessions, the root entry files) is checked by myPKA's
validate-team.py, from the team root, in either install mode.

Exit 0 = compliant. Exit 1 = violations listed on stderr.

Usage: validate-scaffold.py [<vault-root>] [--json]
  --json  print {"root", "ok", "fails", "skipped", "sources"} on stdout
          instead of the OK / SKIPPED lines; FAIL lines still go to stderr.
"""
import json, re, sys
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

JSON = "--json" in sys.argv[1:]
args = [a for a in sys.argv[1:] if a != "--json"]
ROOT = Path(args[0]) if args else Path(__file__).resolve().parents[3]
fails = []
skipped = []   # {"check", "name", "reason"}: a check that could not run here
sources = {}   # check -> the file it read

REQUIRED = [
    "01 Inbox/Outer World/archive",
    "01 Inbox/Scanner Inbox",
    "00 Daily Scratchpad",
    "05 Assets/Images", "05 Assets/Audio", "05 Assets/Documents",
    "04 Inner World/Contacts/People", "04 Inner World/Contacts/Companies",
    "04 Inner World/Journal",
    "04 Inner World/Notes",
    "04 Inner World/My Life/Goals", "04 Inner World/My Life/Key Elements",
    "04 Inner World/My Life/Topics", "04 Inner World/My Life/Projects",
    "04 Inner World/My Life/Habits",
    "03 WiP/_archive",
    # The four buckets of 03 WiP/ (03 WiP/README.md, 2026-09-17). Read from
    # the top, first match wins; Workstreams/ and Projects/ are also the two
    # standing trees, which hold a named folder per process or per Project
    # rather than dated work directly.
    "03 WiP/Workstreams", "03 WiP/AI Team", "03 WiP/Projects", "03 WiP/Operations",
    "07 Databases",
    # No 06 AI Team/ entry: the team's folders are myPKA's and are checked by
    # its validate-team.py. The Templates folder this repo ships is check 12.
]
for rel in REQUIRED:
    if not (ROOT / rel).is_dir():
        fails.append(f"missing required folder: {rel}")

BANNED = {"input", "control", "output", "refine"}
for p in ROOT.rglob("*"):
    if p.is_dir() and not p.name.startswith(".") and p.name.lower() in BANNED:
        fails.append(f"ICOR stage name used as folder (GL-1004): {p.relative_to(ROOT)}")

# The Daily Scratchpad is date-nested exactly like the Journal (GL-1004,
# amended 2026-09-10). This check walked `sp.glob("*.md")` until that date,
# i.e. the ROOM ROOT ONLY, so the moment a vault nested its scratchpads
# correctly the glob matched zero files and the check passed by finding
# nothing. It rglobs now, and the nesting is part of what it asserts.
#
# A collision suffix is a space and a number on a same-minute capture:
# Obsidian's own Unique note starts at " 1", the Scratchpad and AI Chat
# plugins at " 2"; " - Title" is the member naming a capture after the fact, which
# GL-1004 allows because the timestamp stays at the front and keeps the
# folder chronological.
SCRATCHPAD_SHAPES = (
    r"\d{4}-\d{2}-\d{2}\.md",                        # daily note
    r"\d{12}( \d+)?( - .+)?\.md",                     # quick capture, YYYYMMDDHHmm
    r"\d{4}-\d{2}-\d{2}-\d{6}(-\d+)?\.md",          # legacy YYYY-MM-DD-HHmmss
    r"\d{14}(-\d+)?\.md",                            # legacy YYYYMMDDHHMMSS
    r"Untitled( \d+)?\.md",                           # subject note, before it is named
    # The toolbar names a canvas YYYY-MM-DD_canvas; anything after that is
    # the member titling it (`_canvas-test-2`) or Obsidian numbering a copy
    # (` 1`), the same freedom a quick capture has after its timestamp.
    r"\d{4}-\d{2}-\d{2}_canvas([-_ ].*)?\.canvas",
    r".+\.base",                                      # a saved view of the room
)
sp = ROOT / "00 Daily Scratchpad"
if sp.is_dir():
    for f in sp.rglob("*"):
        if not f.is_file() or f.name.startswith("."):
            continue
        if f.name in ("README.md", "_template.md", "INDEX.md"):
            continue
        rel = f.relative_to(sp)
        # A .base is a view of the whole room and belongs at its root.
        if f.suffix == ".base":
            if len(rel.parts) != 1:
                fails.append(f"scratchpad view not at the room root: {rel}")
            continue
        if (len(rel.parts) != 3
                or not re.fullmatch(r"\d{4}", rel.parts[0])
                or not re.fullmatch(r"\d{2}", rel.parts[1])):
            fails.append(f"scratchpad not in YYYY/MM/: {rel}")
            continue
        if not any(re.fullmatch(shape, f.name) for shape in SCRATCHPAD_SHAPES):
            fails.append(
                "scratchpad not named YYYY-MM-DD.md, YYYYMMDDHHmm.md or "
                f"YYYY-MM-DD_canvas.canvas: {rel}")

jr = ROOT / "04 Inner World/Journal"
if jr.is_dir():
    for f in jr.rglob("*.md"):
        if f.name == "README.md":
            continue
        rel = f.relative_to(jr)
        if len(rel.parts) != 3 or not re.fullmatch(r"\d{4}", rel.parts[0]) \
           or not re.fullmatch(r"\d{2}", rel.parts[1]):
            fails.append(f"journal entry not in YYYY/MM/: {rel}")
        elif not re.fullmatch(r"\d{4}-\d{2}-\d{2}_[a-z0-9-]+\.md", f.name):
            fails.append(f"journal entry not YYYY-MM-DD_<slug>.md: {f.name}")

def fm(path):
    txt = path.read_text(encoding="utf-8", errors="ignore")
    if not txt.startswith("---\n"):
        return ""
    end = txt.find("\n---\n", 4)
    return txt[4:end] if end != -1 else ""

projects = ROOT / "04 Inner World/My Life/Projects"
if projects.is_dir():
    # rglob, as check 10 walks Notes/: a project in a subfolder of Projects/
    # escaped this rule until 2.3.0 (member report on 2.2.1, item 6).
    for f in projects.rglob("*.md"):
        if f.name in ("README.md", "_template.md"):
            continue
        front = fm(f)
        m = re.search(r"^goal:\s*(.+)$", front, re.M)
        if not m or "[[" not in m.group(1):
            fails.append(f"project without a goal wikilink (GL-1002: no project without a goal): {f.relative_to(projects).as_posix()}")

goals_dir = ROOT / "04 Inner World/My Life/Goals"
if goals_dir.is_dir():
    for f in goals_dir.rglob("*.md"):           # subfolders too, as above
        if f.name in ("README.md", "_template.md"):
            continue
        m = re.search(r"^status:\s*(\S+)", fm(f), re.M)
        if m and m.group(1) not in ("not-achieved", "achieved"):
            fails.append(f"goal status must be not-achieved|achieved: {f.relative_to(goals_dir).as_posix()} has '{m.group(1)}'")

# --- 7 and 8. planner-habit and planner-routine frontmatter shape (GL-1002) -
DAY_CODES = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")
CADENCES = ("daily", "weekdays", "weekly", "monthly")

def fm_list(front, key):
    """Values of a frontmatter list, inline `[a, b]` or block `- a`.
    None when the key is absent; [] when it is present and empty."""
    m = re.search(r"^%s:[ \t]*(.*)$" % re.escape(key), front, re.M)
    if not m:
        return None
    rest = m.group(1).strip()
    if rest.startswith("["):
        return [v.strip().strip("'\"") for v in rest.strip("[]").split(",") if v.strip()]
    if rest:
        return [rest.strip("'\"")]
    items = []
    for line in front[m.end():].splitlines()[1:]:
        lm = re.match(r"^\s+-\s*(.+)$", line)
        if not lm:
            break
        items.append(lm.group(1).strip().strip("'\""))
    return items

planner_habits = ROOT / "02 Planner/Habits"
if planner_habits.is_dir():
    for f in planner_habits.glob("*.md"):
        if f.name == "README.md":
            continue
        front = fm(f)
        t = re.search(r"^type:\s*(\S+)", front, re.M)
        if not t or t.group(1) != "planner-habit":
            fails.append(f"habit note must carry type: planner-habit (GL-1002): {f.name}")
        if not re.search(r"^name:\s*\S", front, re.M):
            fails.append(f"planner-habit without a name: {f.name}")
        cm = re.search(r"^cadence:\s*(\S+)", front, re.M)
        if not cm:
            fails.append(f"planner-habit without a cadence: {f.name}")
        elif cm.group(1) not in CADENCES:
            fails.append(f"planner-habit cadence must be daily|weekdays|weekly|monthly: {f.name} has '{cm.group(1)}'")
        sm = re.search(r"^status:\s*(\S+)", front, re.M)
        if not sm or sm.group(1) not in ("active", "paused", "archived"):
            fails.append(f"planner-habit status must be active|paused|archived: {f.name}")
        for d in fm_list(front, "cadence_days") or []:
            if d not in DAY_CODES:
                fails.append(f"planner-habit cadence_days must use mon..sun codes: {f.name} has '{d}'")
        mm = re.search(r"^month_day:\s*(\S+)", front, re.M)
        if mm:
            try:
                day = int(mm.group(1))
                if not (1 <= day <= 28):
                    fails.append(f"planner-habit month_day must be 1..28: {f.name} has '{mm.group(1)}'")
            except ValueError:
                fails.append(f"planner-habit month_day must be an integer 1..28: {f.name} has '{mm.group(1)}'")

routines = ROOT / "02 Planner/Routines"
if routines.is_dir():
    for f in routines.glob("*.md"):
        if f.name == "README.md":
            continue
        front = fm(f)
        t = re.search(r"^type:\s*(\S+)", front, re.M)
        if not t or t.group(1) != "planner-routine":
            fails.append(f"routine note must carry type: planner-routine (GL-1002): {f.name}")
        if not re.search(r"^name:\s*\S", front, re.M):
            fails.append(f"routine without a name: {f.name}")
        rt = re.search(r"^routine_type:\s*(\S+)", front, re.M)
        if not rt or rt.group(1) not in ("morning", "afternoon", "evening"):
            fails.append(f"routine_type must be morning|afternoon|evening: {f.name}")
        times = {}
        for key in ("start", "end"):
            km = re.search(r'^%s:\s*"?(\d{2}:\d{2})"?\s*$' % key, front, re.M)
            if km:
                times[key] = km.group(1)
            else:
                fails.append(f"routine {key} must be HH:MM: {f.name}")
        if len(times) == 2 and times["end"] <= times["start"]:
            fails.append(f"routine end must be after start: {f.name} ({times['start']} to {times['end']})")
        days = fm_list(front, "weekdays")
        if days is None:
            fails.append(f"routine without weekdays: {f.name}")
        else:
            for d in days:
                if d not in DAY_CODES:
                    fails.append(f"routine weekdays must use mon..sun codes: {f.name} has '{d}'")
        am = re.search(r"^active:\s*(\S+)", front, re.M)
        if not am or am.group(1) not in ("true", "false"):
            fails.append(f"routine active must be true|false: {f.name}")

# --- 10. type: note shape (GL-1002 Notes; GL-1007) --------------------------
# A note that lives on must say what kind it is and what it is filed under.
# The set of kinds is fixed here AND in GL-1002; a fifth kind is a guideline
# edit first. The link lists are read with fm_list: `[]`, an empty inline
# value and an absent key all count as "no link".
NOTE_TYPES = ("reference", "idea", "outline", "meeting", "draft", "other")
NOTE_LINK_FIELDS = ("projects", "key_elements", "topics")
notes_dir = ROOT / "04 Inner World/Notes"
if notes_dir.is_dir():
    for f in notes_dir.rglob("*.md"):
        if f.name in ("README.md", "_template.md"):
            continue
        front = fm(f)
        t = re.search(r"^type:\s*(\S+)", front, re.M)
        if not t or t.group(1) != "note":
            continue
        nt = re.search(r"^note_type:\s*(\S+)", front, re.M)
        if not nt:
            fails.append(f"note without a note_type (GL-1002: reference|idea|outline|meeting|draft|other): {f.name}")
        elif nt.group(1).strip("'\"") not in NOTE_TYPES:
            fails.append(f"note_type must be reference|idea|outline|meeting|draft|other: {f.name} has '{nt.group(1)}'")
        linked = any(
            any(v.strip() for v in (fm_list(front, k) or []))
            for k in NOTE_LINK_FIELDS)
        if not linked:
            fails.append(f"note filed under nothing (GL-1007: at least one of projects/key_elements/topics): {f.name}")

# --- 11. the daily scratchpad stays blank (GL-1007) -------------------------
# Obsidian's Daily notes core plugin applies `template` to every new daily
# note. The scaffold ships without that key so raw capture starts from an
# empty page; a template sneaking back in would stamp journal properties
# onto every scratchpad. A `template` key with ANY value (even "") is red:
# the key is the setting, the value is not what is being guarded.
dn = ROOT / ".obsidian/daily-notes.json"
if dn.is_file():
    try:
        dn_cfg = json.loads(dn.read_text(encoding="utf-8"))
    except ValueError as exc:
        fails.append(f".obsidian/daily-notes.json is not valid JSON: {exc}")
    else:
        if isinstance(dn_cfg, dict) and "template" in dn_cfg:
            fails.append(".obsidian/daily-notes.json carries a template key "
                         f"({dn_cfg['template']!r}); the daily scratchpad stays blank (GL-1007)")
        # The folder and the format are the two settings GL-1004 spells out,
        # and nothing checked them until 2026-09-11: the shipped file said
        # `YYYY-MM-DD`, so Obsidian wrote flat notes into a room check 3
        # requires to be nested, and GL-1011's links had nothing to resolve
        # to. Both halves are named, because either one alone is wrong.
        DAILY_FOLDER, DAILY_FORMAT = "00 Daily Scratchpad", "YYYY/MM/YYYY-MM-DD"
        if isinstance(dn_cfg, dict):
            if dn_cfg.get("folder") != DAILY_FOLDER:
                fails.append(f".obsidian/daily-notes.json folder is "
                             f"{dn_cfg.get('folder')!r}, not {DAILY_FOLDER!r} (GL-1004)")
            if dn_cfg.get("format") != DAILY_FORMAT:
                fails.append(f".obsidian/daily-notes.json format is "
                             f"{dn_cfg.get('format')!r}, not {DAILY_FORMAT!r}; check 3 "
                             f"requires YYYY/MM/ nesting and GL-1011's [[YYYY-MM-DD]] "
                             f"links need the note named YYYY-MM-DD")

# --- 12. the Templates folder is wired up and its templates are real -------
# GL-1007 "Doing it by hand" tells the member to press Cmd+P, run
# Templates: Insert template, and pick the template for the kind of note.
# That instruction is only true while three things hold: the core plugin
# points at the folder, the templates in it are notes with a GL-1002 type,
# and every template the guideline's `template` column names is on disk.
TEMPLATES_REL = "06 AI Team/AI Team Knowledge/Templates"
templates_dir = ROOT / TEMPLATES_REL
declared_types = None
tj = ROOT / ".obsidian/templates.json"
if not tj.is_file():
    fails.append(".obsidian/templates.json is missing; Templates: Insert "
                 "template has no folder, so the by-hand path in GL-1007 "
                 "has nothing behind it")
else:
    try:
        tj_cfg = json.loads(tj.read_text(encoding="utf-8"))
    except ValueError as exc:
        fails.append(f".obsidian/templates.json is not valid JSON: {exc}")
    else:
        folder = (tj_cfg or {}).get("folder") if isinstance(tj_cfg, dict) else None
        if folder != TEMPLATES_REL:
            fails.append(".obsidian/templates.json folder is "
                         f"{folder!r}; it must be {TEMPLATES_REL!r}")
if templates_dir.is_dir():
    import importlib.util
    _nb_spec = importlib.util.spec_from_file_location(
        "new_base", Path(__file__).resolve().parent / "new-base.py")
    _nb = importlib.util.module_from_spec(_nb_spec)
    _nb_spec.loader.exec_module(_nb)
    declared_types = _nb.gl002_fields(ROOT)
    for f in sorted(templates_dir.glob("*.md")):
        m = re.search(r"^type:\s*(\S+)", fm(f), re.M)
        if not m:
            fails.append(f"template without a type: Templates/{f.name}")
        elif m.group(1).strip("'\"") not in declared_types:
            fails.append(f"template type {m.group(1)!r} is not in GL-1002: "
                         f"Templates/{f.name}")
    gl002_text = (ROOT / "06 AI Team/AI Team Knowledge/Guidelines/"
                  "GL-1002-frontmatter-conventions.md")
    if gl002_text.is_file():
        named = set(re.findall(r"\[\[Templates/([A-Za-z0-9_-]+)\]\]",
                               gl002_text.read_text(encoding="utf-8")))
        for name in sorted(named):
            if not (templates_dir / f"{name}.md").is_file():
                fails.append(f"GL-1002 names [[Templates/{name}]] but "
                             f"{TEMPLATES_REL}/{name}.md does not exist")
else:
    fails.append(f"missing required folder: {TEMPLATES_REL}")

# --- 13. every list property is multitext in the Properties panel ----------
# A wikilink list is only a relation while Obsidian treats it as a list: as
# `text` the whole `["[[A]]", "[[B]]"]` is one string, the `[[` suggestion
# does not fire, and Bases reads one value where there are two. Which
# properties are lists is not restated here: it is read from the templates,
# which GL-1002 names as the one place the field list is spelled out as
# YAML, so adding a list field to a template extends this check by itself.
#
# THREE PROPERTIES ARE NOT OURS TO TYPE. Obsidian's MetadataTypeManager
# owns `tags` and `aliases`: it ignores whatever types.json says for them
# and rewrites the file with its own names the first time any property
# type changes in the vault (Flint, 2026-09-09). Demanding `multitext`
# there would ship a check that goes red on its own, in a member's vault,
# for something the member did not do and cannot fix, which is worse than
# no check at all. So the wanted value for those two is Obsidian's own,
# and `cssclasses` (a real list Obsidian does not rename) stays multitext.
RESERVED_TYPES = {"tags": "tags", "aliases": "aliases", "cssclasses": "multitext"}
if templates_dir.is_dir():
    list_props = set()
    for f in sorted(templates_dir.glob("*.md")):
        front = fm(f)
        for i, line in enumerate(front.splitlines()):
            km = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):[ \t]*(.*)$", line)
            if not km:
                continue
            value = km.group(2).strip()
            rest = front.splitlines()[i + 1:i + 2]
            if value.startswith("[") or (not value and rest
                                         and re.match(r"^\s+-\s", rest[0])):
                list_props.add(km.group(1))
    tyj = ROOT / ".obsidian/types.json"
    if not tyj.is_file():
        fails.append(".obsidian/types.json is missing; every list property "
                     "falls back to text and the Properties panel stops "
                     "offering the [[ suggestion")
    else:
        try:
            ty_cfg = json.loads(tyj.read_text(encoding="utf-8"))
        except ValueError as exc:
            fails.append(f".obsidian/types.json is not valid JSON: {exc}")
        else:
            declared_prop = (ty_cfg or {}).get("types") \
                if isinstance(ty_cfg, dict) else None
            if not isinstance(declared_prop, dict):
                fails.append(".obsidian/types.json has no `types` mapping")
            else:
                for p in sorted(list_props):
                    want = RESERVED_TYPES.get(p, "multitext")
                    got = declared_prop.get(p)
                    if got != want:
                        why = (" (Obsidian owns this property name and "
                               "rewrites any other value)"
                               if p in RESERVED_TYPES and want != "multitext"
                               else "; a list property must be 'multitext'")
                        fails.append(
                            f".obsidian/types.json declares {p!r} as "
                            f"{got!r}, it must be {want!r}{why}")

# Checks 5 and 9 (session-log and task nesting, agent folders and their
# myicor_id) moved to myPKA's validate-team.py with the split: they are about
# the team's tree, which in mode B is not in this folder at all.

# --- 6. no folder inside a room renders unstyled -----------------------
# Every rule that colours the file tree reduces to predicates on one string,
# the folder's data-path, so a match can be decided exactly here without a
# browser. The rules live in the ICOR for Life - INKLINE theme since 1.4.0
# (src/60-rooms.css there; the icor-rooms.css snippet carried them before).
#
# WHY THIS CHECK READS A SOURCE OR SAYS SO. From 1.4.0 to 1.13.0 it read the
# retired snippet behind `if snippet.is_file()`, so in every shipped vault
# the read was skipped and the check passed by covering nothing, the exact
# failure the comment below warns about (reported by Andrew Gillley,
# 2026-09-07, from a 1.10.2 vault). Now: the active theme first (the one
# appearance.json names), then any theme whose css carries room rules,
# then the snippet; and with NONE of them present the check is SKIPPED,
# said so on stdout and in --json, and never counted as passed.
#
# THE THEME'S GRAMMAR, which the snippet's regex could not read: the
# folder-title compound is `.nav-folder-title:is(A, B, ...)` or
# `.nav-folder-title:not([data-icor-kind])[data-path...]`, under a body-level
# guard (`body:not(.icor-rooms-off)`), and the glyph is no longer a literal
# `mask-image:` on a `::before` rule but `--room-icon` set on the title and
# drawn by one mechanism rule. So this evaluates the compound as CSS does
# (:is/:where = any, :not = none, attribute selectors on data-path; a
# `data-icor-kind` attribute is never present, because that is the plugin
# speaking and this check models the theme alone), and a compound it cannot
# read is a FAIL naming the selector, never a silent miss: a new selector
# shape in the theme must stop this check the way it stops the theme build.

def room_css_source():
    """The file whose rules decide how the tree renders, or None."""
    themes = sorted((ROOT / ".obsidian/themes").glob("*/theme.css"))
    active = None
    app = ROOT / ".obsidian/appearance.json"
    if app.is_file():
        try:
            active = json.loads(app.read_text(encoding="utf-8")).get("cssTheme")
        except (ValueError, AttributeError):
            active = None
    themes.sort(key=lambda p: (p.parent.name != active, p.parent.name))
    for th in themes:
        if "--room-color" in th.read_text(encoding="utf-8", errors="ignore"):
            return th
    snippet = ROOT / ".obsidian/snippets/icor-rooms.css"
    return snippet if snippet.is_file() else None

class Unparseable(Exception):
    pass

ATTR = re.compile(r'\[([a-zA-Z-]+)(?:(\^|\$|\*|~|\|)?="([^"]*)")?\]')

def split_top(s, sep):
    """Split on `sep` outside brackets and parentheses."""
    parts, depth, cur = [], 0, []
    for ch in s:
        if ch in "([":
            depth += 1
        elif ch in ")]":
            depth -= 1
        if depth == 0 and ch in sep:
            parts.append("".join(cur)); cur = []
        else:
            cur.append(ch)
    parts.append("".join(cur))
    return [x.strip() for x in parts if x.strip()]

def simples(comp):
    """A compound selector as its simple selectors, brackets honoured."""
    out, i = [], 0
    while i < len(comp):
        ch = comp[i]
        if ch == "[":
            j = comp.find("]", i)
            if j == -1:
                raise Unparseable(comp)
            out.append(comp[i:j + 1]); i = j + 1
        elif ch == ":":
            m = re.match(r"::?[a-zA-Z-]+", comp[i:])
            if not m:
                raise Unparseable(comp)
            k = i + len(m.group(0))
            if k < len(comp) and comp[k] == "(":
                depth, j = 0, k
                while j < len(comp):
                    depth += (comp[j] == "(") - (comp[j] == ")")
                    if depth == 0:
                        break
                    j += 1
                if depth != 0:
                    raise Unparseable(comp)
                out.append(comp[i:j + 1]); i = j + 1
            else:
                out.append(m.group(0)); i = k
        else:
            m = re.match(r"[.#]?[a-zA-Z0-9_*-]+", comp[i:])
            if not m:
                raise Unparseable(comp)
            out.append(m.group(0)); i += len(m.group(0))
    return out

def hit(value, op, val):
    return (value.startswith(val) if op == "^" else
            value.endswith(val)   if op == "$" else
            val in value          if op == "*" else
            value == val          if op is None else
            val in value.split()  if op == "~" else
            value == val or value.startswith(val + "-"))

def compound_matches(comp, attrs):
    """Does a compound (no combinators) match an element with `attrs`?
    States this check does not model (:hover, .is-collapsed, a type
    selector) are False; the two logical pseudo-classes evaluate."""
    ok = True
    for s in simples(comp):
        if s.startswith("["):
            name, op, val = ATTR.fullmatch(s).groups() if ATTR.fullmatch(s) else (None, None, None)
            if name is None:
                raise Unparseable(comp)
            v = (name in attrs) and (val is None or hit(attrs[name], op, val))
        elif s.startswith("::"):
            v = True   # a pseudo-element paints the element; it does not filter it
        elif s.startswith(":"):
            m = re.fullmatch(r":([a-z-]+)\((.*)\)", s, re.S)
            if m and m.group(1) in ("is", "where", "matches"):
                v = any(compound_matches(c, attrs) for c in split_top(m.group(2), ","))
            elif m and m.group(1) == "not":
                v = not any(compound_matches(c, attrs) for c in split_top(m.group(2), ","))
            elif m:
                raise Unparseable(comp)
            else:
                v = False  # :hover, :focus, :active: a state, not a folder
        elif s in (".nav-folder-title", "*"):
            v = True
        else:
            v = False      # another class, an id, a type: not the title as such
        ok = ok and v
    return ok

def title_rule(sel):
    """(the folder-title compound, the parts after it) for one selector,
    or (None, None) when the selector is not about a folder title."""
    parts = [p for p in split_top(sel, " \t\n") if p not in (">", "+", "~")]
    for i, part in enumerate(parts):
        try:
            first = simples(part)[0]
        except Unparseable:
            first = None
        if first == ".nav-folder-title":
            return part, parts[i + 1:]
    return None, None

source = room_css_source()
if source is None:
    skipped.append({
        "check": 6, "name": "file-tree styling",
        "reason": "no rule source in the vault: no .obsidian/themes/*/theme.css "
                  "carries room rules (--room-color) and "
                  ".obsidian/snippets/icor-rooms.css is absent; "
                  "folder colours and glyphs were not checked"})
else:
    sources["6"] = source.relative_to(ROOT).as_posix()
    css = re.sub(r"/\*.*?\*/", "", source.read_text(encoding="utf-8"), flags=re.S)
    rules = []   # (title compound, descendant parts, body)
    unreadable = []
    for sel_text, body in re.findall(r"([^{}]+)\{([^{}]*)\}", css):
        if "data-path" not in sel_text:
            continue
        for sel in split_top(sel_text, ","):
            sel = sel.strip()
            if not sel or sel.startswith("@"):
                continue
            try:
                comp, rest = title_rule(sel)
                if comp is not None:
                    compound_matches(comp, {"data-path": ""})   # parse it once, now
                    rules.append((comp, rest, body))
            except Unparseable:
                if sel not in unreadable:
                    unreadable.append(sel)
    for sel in unreadable:
        fails.append(f"check 6 cannot read a file-tree selector in {sources['6']}: {sel}")

    def resolves(path):
        colour = glyph = False
        attrs = {"data-path": path}
        for comp, rest, body in rules:
            if not compound_matches(comp, attrs):
                continue
            if "--room-color:" in body:
                colour = True
            if "--room-icon:" in body:
                glyph = True     # the theme: the glyph is a custom property
            if any("::before" in r for r in rest) and re.search(r"(?<![\w-])mask-image:\s*(?!var\()", body):
                glyph = True     # the snippet: a literal mask on ::before
        return colour, glyph

    rooms = sorted(d.name for d in ROOT.iterdir()
                   if d.is_dir() and re.fullmatch(r"\d\d .+", d.name))
    # SCOPE IS DERIVED FROM THE FLOOR, NEVER RESTATED.
    #
    # This used to carry its own `/20\d\d(/|$)` regex to skip date-nested
    # data folders, which was a second, hand-maintained copy of a rule the CSS
    # already states as `:not(:where([data-path*="/20"]))`. The two disagreed
    # at exactly one folder shape: the chat plugin's session folders are named
    # `2026-08-30_1312_...`, so `/2026` is followed by `-`, which the CSS
    # excludes and this regex did not match. Every vault that had held one
    # conversation failed this check.
    #
    # The standing rule, so the two can never disagree again: THE CSS IS THE
    # AUTHORITY. It cannot express "path segment", so its approximation IS the
    # rule, and this check may only ever be LOOSER than the CSS, never
    # stricter. `compound_matches` evaluates the `:not()` as CSS does, so
    # `colour` below is the floor's own answer and there is nothing left to
    # restate.
    #
    # Two clauses, and the first is why the check keeps its purpose. A room
    # folder is ALWAYS in scope, so a new `08 ` room nobody styled still
    # fails. The room itself was previously never evaluated at all - `rglob`
    # yields descendants only - so an unstyled room was caught indirectly
    # through its children, and dropping the regex without adding the room
    # itself would have quietly retired the check's main job.
    for room in rooms:
        for d in [ROOT / room, *(ROOT / room).rglob("*")]:
            rel = str(d.relative_to(ROOT))
            if not d.is_dir() or d.name.startswith("."):
                continue
            colour, glyph = resolves(rel)
            if "/" in rel and not colour:
                continue   # a descendant the floor declined; so does this check
            if not (colour and glyph):
                missing = " and ".join(
                    x for x, ok in (("colour", colour), ("glyph", glyph)) if not ok)
                fails.append(
                    f"folder renders unstyled in the file tree (no {missing} "
                    f"from {sources['6']}): {rel}")

# Check 15 (the root entry contract) moved to myPKA's validate-team.py: the
# entry files ship with the team, not with this folder.

# --- 16. the shipped 03 WiP buckets are empty except their README ---------
# 03 WiP/ is the MEMBER's working surface, so the Scaffold hands it over with
# the buckets and their READMEs and nothing else in them (Tom, 2026-09-18).
# Within hours of the buckets existing a session wrote a hire workup straight
# into 03 WiP/2026-09-17-ada-hire/ in the source repo, where it was untracked,
# invisible to `git status`-by-habit, and one `git add` away from shipping to
# every member as somebody else's leftover work. "Remember not to write there"
# is not a control; this is.
#
# WHY THIS IS SCOPED, AND WHY A SKIP IS LOUD. In a lived-in vault a full
# 03 WiP/ is the room working exactly as designed, and a check that failed
# there would be ripped out within a week, taking the release gate with it.
# So it runs only in the Scaffold's own SOURCE REPO, identified by the release
# workflow that cuts the release: .github/ is in no manifest and ships in no
# release, so its presence means this tree is the one the release is built
# from. Everywhere else the check reports itself SKIPPED, on stdout and in
# --json, the same way check 6 does, so it can never pass by covering nothing.
#
# FILES ONLY. The standing trees (Workstreams/, Projects/) hold a named folder
# per process or per Project, and an empty folder is not in a git tree at all,
# so a directory is never the failure. A file in one is.
wip = ROOT / "03 WiP"
if not (ROOT / ".github/workflows/release.yml").is_file():
    skipped.append({"check": 16, "name": "03 WiP buckets ship empty",
                    "reason": "not the Scaffold source repo (no .github/workflows/"
                              "release.yml); a member's 03 WiP/ is meant to fill up"})
elif wip.is_dir():
    sources["16"] = ".github/workflows/release.yml"
    for f in sorted(wip.rglob("*")):
        if not f.is_file() or f.name.startswith("."):
            continue
        if f.name == "README.md":
            continue
        fails.append(
            "03 WiP ships empty except its READMEs, so this file must not be in "
            f"the Scaffold (move it to your own vault): {f.relative_to(ROOT)}")

for msg in fails:
    print(f"FAIL {msg}", file=sys.stderr)
if JSON:
    print(json.dumps({"root": str(ROOT), "ok": not fails, "fails": fails,
                      "skipped": skipped, "sources": sources}, indent=2))
else:
    for s in skipped:
        print(f"SKIPPED check {s['check']} ({s['name']}): {s['reason']}")
    if not fails:
        print(f"OK scaffold at {ROOT} is compliant"
              + (f" ({len(skipped)} check skipped, see above)" if skipped else ""))
sys.exit(1 if fails else 0)
