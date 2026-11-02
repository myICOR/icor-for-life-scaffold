#!/usr/bin/env python3
"""Answer the six everyday life questions from ONE regenerated file.

Usage:
  life-snapshot.py [<vault-root>] [--json] [--write] [--brief]

  (no flag)  the same short brief a person reads, on stdout
  --json     the whole snapshot on stdout, for a machine
  --write    the snapshot to .icor-for-life/scripts/snapshot.json, which the
             session-start hook, the skill prerun and the AI Chat plugin read
  --brief    the short brief only (about 20 lines), for the hook

The six questions: my goals, the projects I should focus on, my weekly
priorities, my highlight today, my key elements, the topics with my recent attention.
Five of the six are a script answer. The sixth (focus) is a script reading a
decision the user made and stored as `focus_rank`; this script never decides
which projects are in focus and never picks a highlight.

check-quality.py answers "is what is in the vault any good". This answers
"what is in my life right now". Two questions, two scripts, on purpose.

Runs in BOTH vaults. The private vault stores foreign keys as slugs and the
public one as quoted wikilinks; FIELDS below carries both spellings of every
field name and the resolver accepts both value shapes, so there is one script
and no per-vault branch beyond that one dict.

The report shape is schema 1, documented in Scripts/README.md, and is a
contract with its readers: field names and order do not change inside a
schema version.

Exit 0 = a snapshot was produced (read `degraded` before trusting a gap).
Exit 1 = refused: the path is not a vault root, the file cannot be written,
or a secret-shaped value would have been written. A missing report is never
a green: an absent file means the script did not run, never that the user
has no goals.
"""
import argparse
import datetime
import importlib.util
import json
import os
import re
import sys
import time
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

SCHEMA = 1

# The thresholds. Judgement, which is why they are here and not in a
# guideline, and in ONE place so they can be moved in one line.
# Approved by the user on 2026-09-15 (decision th5st).
THRESHOLDS = {
    "topics_shown": 5,          # the ranking shows this many, score above 0 only
    "attention_hot_score": 6,   # at or above this a topic is hot: two entries this week, or one this week and one last
    "focus_max": 3,             # more projects than this carrying focus_rank is a finding, not a ranking
    "weekly_goals_max": 5,      # more than this in one week is a finding; the week does not get longer
    "stale_after_hours": 6,     # a reader treats an older snapshot as stale and says so
}

# How much one dated link event is worth, by its age in days on the day the
# script runs. Older than the last row is not counted at all. Separate from
# THRESHOLDS on purpose: these are the scoring rule, not a cutoff to move.
WEIGHTS = (
    (7, 3),    # 0 to 7 days: this week
    (14, 2),   # 8 to 14 days: last week
    (30, 1),   # 15 to 30 days: this month
)
WINDOW_DAYS = WEIGHTS[-1][0]

# Where each room is. A room that does not exist is reported in `degraded`,
# never crashed on.
ROOMS = {
    "goals": "04 Inner World/My Life/Goals",
    "projects": "04 Inner World/My Life/Projects",
    "key_elements": "04 Inner World/My Life/Key Elements",
    "topics": "04 Inner World/My Life/Topics",
    "journal": "04 Inner World/Journal",
    "notes": "04 Inner World/Notes",
    "scratchpad": "00 Daily Scratchpad",
    "planner": "02 Planner",
    "planner_weeks": "02 Planner/Weeks",
}

# The per-vault field-name map, one line per logical field. The first name
# found on the note wins. Private vault spellings first, public second,
# because the private vault is the one with the data today.
FIELDS = {
    "goal_key_element": ("key_element", "key_elements"),        # private singular slug, public plural wikilinks
    "goal_projects": ("linked_projects", "projects"),           # the carriers doctrine: a goal is carried by projects
    "goal_habits": ("linked_habits", "habits"),                 # or by habits
    "goal_workstreams": ("linked_workstreams", "workstreams"),  # or by a workstream (GL-002 v1.52 / GL-1002 2026-09-15)
    "project_goal": ("linked_goals", "goal", "goals"),          # private list, public one quoted wikilink
    "project_key_element": ("key_element", "key_elements"),     # same split as the goal room
    "topic_key_element": ("key_element", "key_elements"),       # a topic hangs under one key element
    "journal_topics": ("linked_topics", "topics"),              # the primary attention signal
    "journal_projects": ("linked_projects", "projects"),        # project attention
    "journal_goals": ("linked_goals", "goals"),                 # read for completeness, not scored separately
    "journal_key_element": ("key_element", "key_elements"),     # private writes one, public writes a list
    "note_topics": ("topics", "linked_topics"),                 # a filed note is weaker attention
    "note_key_elements": ("key_elements", "linked_key_elements", "key_element"),
    "note_projects": ("projects", "linked_projects"),
    "planner_link": ("linked_note", "linked_projects"),         # blocked today: no planner item carries either
}

# Which status values mean "still open", per room. Both vaults' sets are in
# one place; a vault only ever carries its own spellings.
OPEN_STATUS = {
    "goal": {"planning", "active", "not-achieved"},   # private planning/active, public not-achieved
    "project": {"planning", "active"},                # public ships active only
    "key_element": {"active", "dormant"},             # archived is hidden; an absent status is shown
}
# A status nobody wrote is not a closed status. An entity with no `status`
# field at all is shown, because the public schema has none on some types.
CLOSED_GOAL_STATUS = {"done", "achieved", "abandoned", "cancelled"}

SKIP_NAMES = {"README.md", "INDEX.md", "_template.md", "template.md"}
# Never read for attention, at any depth. The team's own work record is not
# the user's attention, and a WiP folder is a draft nobody lives in.
SKIP_PARTS = {"06 AI Team", "03 WiP", "05 Assets", "07 Databases", "01 Inbox",
              "_archive", "archive", "Highlights", "node_modules"}

WIKILINK = re.compile(r"!?\[\[([^\]\n]+)\]\]")
DATE_PREFIX = re.compile(r"^(\d{4}-\d{2}-\d{2})")
ISO_WEEK = re.compile(r"^\d{4}-W\d{2}$")
# The two sentinels in the week note. Names are Iris's ruling of
# 2026-09-15: a weekly outcome is a Weekly Priority, the day one is the
# Daily Highlight, and the bare word "highlight" stays with the PDF
# sense it already had. GL-1002 "Planner weeks" is the SSOT.
PRIORITIES_SENTINEL = "<!-- weekly-priorities: schema=checklist -->"
HIGHLIGHTS_SENTINEL = "<!-- daily-highlights: schema=highlight -->"
CHECKBOX = re.compile(r"^\s*-\s*\[([ xX])\]\s*(.*\S)\s*$")

# Token shapes that must never reach the file. LIFTED VERBATIM from
# `_SECRET_PATTERNS` in write-guard.py (which lifted it from
# outbound-write-guard.py) so the guard and this script cannot disagree
# about what a secret is. Vex F1, 2026-09-15: the previous hand-written
# tuple covered 6 of the guard's 13 families, and a Stripe-shaped value in
# a weekly checklist line was written to snapshot.json with exit 0. That
# matters more than a normal note leak, because the brief built from this
# file enters model context at every session start.
#
# Every pattern matches a VALUE, never a variable NAME: naming a secret is
# normal practice in this vault and must never fire. Two are this script's
# own and stay: `Bearer` (a header pasted into a note) and the AWS access
# key id, neither of which the guard carries. When the guard's list moves,
# move this one in the same change.
#
# No placeholder allowlist, deliberately. `_looks_placeholder` in the guard
# exists because a guard that blocks a member's documentation edit is
# worse than the leak; here a false refusal costs one snapshot and prints
# the reason, so the stricter side is the right one.
SECRET_SHAPES = (
    ("jwt", re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}")),
    ("supabase_secret", re.compile(r"\bsb_secret_[A-Za-z0-9_-]{16,}")),
    ("resend_key", re.compile(r"\bre_[A-Za-z0-9]{4,32}_[A-Za-z0-9]{16,}")),
    ("resend_key_ctx", re.compile(
        r"(?i)(?:resend[a-z0-9_\-]*\s*[:=]\s*[\"']?|bearer\s+)(re_[A-Za-z0-9_]{16,})")),
    # `(?!ant-)` so an Anthropic key is not also reported as an OpenAI one:
    # the shapes overlap, and a hit naming the wrong vendor sends whoever
    # reads it to rotate the wrong credential.
    ("openai_key", re.compile(r"\bsk-(?!ant-)(?:proj-)?[A-Za-z0-9_-]{24,}")),
    ("anthropic_key", re.compile(r"\bsk-ant-[A-Za-z0-9_-]{24,}")),
    ("github_token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}")),
    ("slack_token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{12,}")),
    ("stripe_key", re.compile(r"\b[sr]k_(?:live|test)_[A-Za-z0-9]{20,}")),
    ("telegram_token", re.compile(r"\b\d{8,10}:[A-Za-z0-9_-]{33,}")),
    ("google_refresh", re.compile(r"\b1//[A-Za-z0-9_-]{25,}")),
    ("pg_dsn_password", re.compile(r"\bpostgres(?:ql)?://[^\s:/@]+:[^\s@'\"]{6,}@")),
    ("private_key_block", re.compile(
        r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY-----")),
    ("generic_secret_assignment", re.compile(
        r"\b[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)*_"
        r"(?:KEY|SECRET|TOKEN|PASSWORD|PASSWD|PWD|DSN|CREDENTIALS|APIKEY)"
        r"\s*[=:]\s*[\"']?([A-Za-z0-9_\-./+]{16,})")),
    # This script's own two, kept: the guard does not carry either.
    ("aws_access_key_id", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("bearer_header", re.compile(r"\bBearer\s+[A-Za-z0-9._-]{24,}")),
)

# A version string and nothing else. `.icor-for-life/VERSION` is the one
# file whose whole content lands in the JSON unparsed, so it is the one
# file that gets a shape check (Vex F3): a plugin bug that writes an env
# line or a whole config into it must become "unknown", not a payload.
VERSION_SHAPE = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]{1,32})?$")


# --- the readers -----------------------------------------------------------
# One reader, not two. Where check-quality.py sits beside this script (the
# public Scaffold) its readers are imported, so a correction to the link
# resolver lands in both scripts at once. Where it does not (this private
# vault, which has no check-quality.py), the identical fallback below runs.
# test-life-snapshot.py asserts the two paths agree wherever both exist.

def _load_check_quality():
    path = HERE / "check-quality.py"
    if not path.is_file():
        return None
    try:
        spec = importlib.util.spec_from_file_location("check_quality", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        for name in ("split_front", "parse_front", "as_list", "link_name",
                     "norm", "truthy", "resolver", "blank_code"):
            if not hasattr(mod, name):
                return None
        return mod
    except Exception:
        return None


_CQ = _load_check_quality()


def _fb_split_front(text):
    """(frontmatter text, body). Both may be empty; never raises."""
    if not text.startswith("---\n"):
        return "", text
    end = text.find("\n---\n", 4)
    if end == -1:
        return "", text
    return text[4:end], text[end + 5:]


def _fb_unquote(v):
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        v = v[1:-1]
    return v.strip()


def _fb_split_items(s):
    """Split an inline list on commas that are not inside brackets or quotes."""
    parts, cur, depth, quote = [], [], 0, None
    for ch in s:
        if quote:
            if ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
        elif ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
        elif ch == "," and depth == 0:
            parts.append("".join(cur))
            cur = []
            continue
        cur.append(ch)
    parts.append("".join(cur))
    return parts


def _fb_strip_comment(rest):
    """A frontmatter value without its trailing `# comment`: check-quality.py's
    strip_comment, for a folder without it."""
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


def _fb_parse_front(front):
    """{key: value} for a flat frontmatter block, values kept as written."""
    out = {}
    lines = front.splitlines()
    i = 0
    while i < len(lines):
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):(.*)$", lines[i])
        if not m:
            i += 1
            continue
        key, rest = m.group(1), _fb_strip_comment(m.group(2)).strip()
        if rest.startswith("[") and rest.endswith("]"):
            out[key] = [_fb_unquote(v) for v in _fb_split_items(rest[1:-1])
                        if v.strip()]
        elif rest:
            out[key] = _fb_unquote(rest)
        else:
            items, j = [], i + 1
            while j < len(lines) and re.match(r"^\s+-\s*", lines[j]):
                items.append(_fb_unquote(_fb_strip_comment(re.sub(r"^\s+-", "", lines[j]))))
                j += 1
            out[key] = items if items else ""
            i = j - 1
        i += 1
    return out


def _fb_as_list(value):
    if isinstance(value, list):
        return [v for v in value if str(v).strip()]
    return [value] if str(value).strip() else []


def _fb_link_name(raw):
    """The note a wikilink points at: no alias, no heading, no block id."""
    s = str(raw).strip()
    m = re.fullmatch(r"!?\[\[(.+?)\]\]", s)
    if m:
        s = m.group(1)
    s = s.split("|", 1)[0]
    s = re.split(r"[#^]", s, maxsplit=1)[0]
    return s.strip()


def _fb_norm(s):
    return re.sub(r"\s+", " ", str(s).strip()).casefold()


def _fb_truthy(v):
    return str(v).strip().strip("\"'").lower() in ("true", "yes", "1")


def _fb_shorter(a, b):
    if a is None:
        return b
    return min((a, b), key=lambda r: (len(r.parts), len(r.as_posix()),
                                      r.as_posix()))


def _fb_resolver(files, notes=None):
    """Obsidian-shaped link resolution: full path, filename, stem, alias."""
    by_path, by_name, by_stem, by_alias = {}, {}, {}, {}
    for rel in files:
        for key in (_fb_norm(rel.as_posix()),
                    _fb_norm(rel.with_suffix("").as_posix())):
            by_path[key] = _fb_shorter(by_path.get(key), rel)
        by_name[_fb_norm(rel.name)] = _fb_shorter(by_name.get(_fb_norm(rel.name)), rel)
        by_stem[_fb_norm(rel.stem)] = _fb_shorter(by_stem.get(_fb_norm(rel.stem)), rel)
    for rel, n in (notes or {}).items():
        for al in _fb_as_list(n.get("front", {}).get("aliases", "")):
            key = _fb_norm(_fb_link_name(al))
            if key:
                by_alias[key] = _fb_shorter(by_alias.get(key), rel)

    def resolve(name):
        k = _fb_norm(name)
        if not k:
            return None
        return (by_path.get(k) or by_name.get(k) or by_stem.get(k)
                or by_alias.get(k))
    return resolve


_CODE_FENCE = re.compile(r"(?ms)^[ \t]*(`{3,}|~{3,})[^\n]*\n.*?(?:^[ \t]*\1[^\n]*$|\Z)")
_CODE_SPAN = re.compile(r"`[^`\n]*`")


def _fb_blank_code(text):
    """The note with code blanked, not deleted, so offsets do not move."""
    def wipe(m):
        return "".join(c if c == "\n" else " " for c in m.group(0))
    return _CODE_SPAN.sub(wipe, _CODE_FENCE.sub(wipe, text))


split_front = getattr(_CQ, "split_front", None) or _fb_split_front
parse_front = getattr(_CQ, "parse_front", None) or _fb_parse_front
as_list = getattr(_CQ, "as_list", None) or _fb_as_list
link_name = getattr(_CQ, "link_name", None) or _fb_link_name
norm = getattr(_CQ, "norm", None) or _fb_norm
truthy = getattr(_CQ, "truthy", None) or _fb_truthy
resolver = getattr(_CQ, "resolver", None) or _fb_resolver
blank_code = getattr(_CQ, "blank_code", None) or _fb_blank_code
READER_SOURCE = "check-quality.py" if _CQ else "built-in fallback"


# --- small helpers ---------------------------------------------------------

def first_field(front, key):
    """The value of the first spelling of a logical field the note carries."""
    for name in FIELDS[key]:
        if name in front and as_list(front.get(name, "")):
            return as_list(front[name])
    return []


def iso_date(value):
    """A date, or None. Accepts a bare date and a timestamp; never guesses."""
    s = str(value).strip().strip("\"'")
    if not s or s.lower() in ("null", "none", "~"):
        return None
    try:
        return datetime.date.fromisoformat(s[:10])
    except ValueError:
        return None


def date_of(rel, front, keys):
    """The date a note carries, else its filename prefix. Never its mtime:
    mtime moves when a script rewrites frontmatter or a sync lands on a second
    device, and none of that is the user's attention."""
    for k in keys:
        d = iso_date(front.get(k, ""))
        if d:
            return d
    m = DATE_PREFIX.match(rel.stem)
    if m:
        return iso_date(m.group(1))
    return None


def weight_for(age_days):
    if age_days < 0:
        return 0        # a future-dated file is not attention that happened
    for limit, w in WEIGHTS:
        if age_days <= limit:
            return w
    return 0


def skip_rel(rel):
    parts = set(rel.parts[:-1])
    if parts & SKIP_PARTS:
        return True
    if any(p.startswith(".") for p in rel.parts):
        return True
    return rel.name in SKIP_NAMES


def read_note(root, rel):
    try:
        text = (root / rel).read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None
    front, body = split_front(text)
    return {"front": parse_front(front), "body": body,
            "prose": front + blank_code(body)}


def walk_md(root, folder, flat=False):
    """Every markdown note under a room, skipping what is never read.

    A SYMLINKED `.md` is skipped, at every depth (Vex F5, 2026-09-15). It
    was the one way text from outside the vault reached the brief and, once
    the session-start hook runs this unattended, model context: plant a
    link in a room and its frontmatter `name` is read as a goal. The room
    boundary has to be a real boundary, not a naming convention. Nothing
    legitimate in this vault is a symlinked note, so the cost is zero.

    `flat=True` reads the room's direct children only, which is what an
    entity room IS: one file per concept, never nested (AGENTS.md hard rule
    5). It is also what keeps a project's own working subfolder, and an
    `_archive/`, from being counted as more projects.
    """
    base = root / folder
    if not base.is_dir():
        return []
    out = []
    for p in sorted(base.glob("*.md") if flat else base.rglob("*.md")):
        if p.is_symlink():
            continue        # Vex F5, see the docstring
        rel = p.relative_to(root)
        if skip_rel(rel):
            continue
        out.append(rel)
    return out


def display_name(rel, front):
    for k in ("name", "title"):
        v = str(front.get(k, "")).strip().strip("\"'")
        if v:
            return v
    return rel.stem


def is_stale(report, now=None):
    """The reader's rule, in code: is this snapshot old enough to say so.
    A reader that cannot parse `generated_at` treats the file as stale."""
    now = now or datetime.datetime.now(datetime.timezone.utc)
    try:
        gen = datetime.datetime.strptime(report["generated_at"],
                                         "%Y-%m-%dT%H:%M:%SZ")
        gen = gen.replace(tzinfo=datetime.timezone.utc)
    except (KeyError, TypeError, ValueError):
        return True
    hours = (now - gen).total_seconds() / 3600.0
    if hours >= THRESHOLDS["stale_after_hours"]:
        return True
    return report.get("generated_local_date") != datetime.date.today().isoformat()


def secret_findings(text):
    """Every secret-shaped token in the serialized report, by pattern name."""
    hits = []
    for name, rx in SECRET_SHAPES:
        if rx.search(text):
            hits.append(name)
    return hits


# --- the run ---------------------------------------------------------------

def run(root, today=None):
    today = today or datetime.date.today()
    degraded = []
    findings = []

    def degrade(source, reason, effect):
        degraded.append({"source": source, "reason": reason, "effect": effect})

    def find(fid, path, message, action):
        findings.append({"id": fid, "path": path, "message": message,
                         "action": action})

    # --- the rooms, read once ---------------------------------------------
    entities = {}          # kind -> {rel: note}
    for kind in ("goals", "projects", "key_elements", "topics"):
        folder = ROOMS[kind]
        if not (root / folder).is_dir():
            degrade(kind, "no folder at %s" % folder,
                    "the %s list is empty" % kind.replace("_", " "))
            entities[kind] = {}
            continue
        recs = {}
        for rel in walk_md(root, folder, flat=True):
            n = read_note(root, rel)
            if n is not None:
                recs[rel] = n
        entities[kind] = recs

    all_entity = {}
    for kind, recs in entities.items():
        for rel, n in recs.items():
            all_entity[rel] = n
    resolve = resolver(list(all_entity), all_entity)

    kind_of = {}
    for kind, recs in entities.items():
        for rel in recs:
            kind_of[rel] = kind

    # --- attention: one event per source note per target -------------------
    events = {}            # target rel -> [(date, source kind)]
    sources_counted = {"journal": 0, "scratchpad": 0, "notes": 0, "planner": 0}

    def add_events(rel_source, when, kind, names, prose=None):
        """One event per target, however many times the source names it."""
        targets = set()
        for raw in names:
            t = resolve(link_name(raw))
            if t is not None and t != rel_source:
                targets.add(t)
        if prose:
            for raw in WIKILINK.findall(prose):
                t = resolve(link_name(raw))
                if t is not None and t != rel_source:
                    targets.add(t)
        for t in targets:
            events.setdefault(t, []).append((when, kind))
        return bool(targets)

    # Journal: only the months that touch the window, so a vault with ten
    # years of entries costs the same as a vault with one.
    journal_dir = root / ROOMS["journal"]
    if not journal_dir.is_dir():
        degrade("journal", "no folder at %s" % ROOMS["journal"],
                "attention cannot be measured; every score is 0")
    else:
        months = set()
        for i in range(WINDOW_DAYS + 1):
            d = today - datetime.timedelta(days=i)
            months.add((d.strftime("%Y"), d.strftime("%m")))
        cand = [journal_dir / y / m for y, m in sorted(months)]
        rels = []
        if any(p.is_dir() for p in cand):
            for p in cand:
                if not p.is_dir():
                    continue
                for f in sorted(p.glob("*.md")):
                    if f.is_symlink():
                        continue        # Vex F5
                    rel = f.relative_to(root)
                    if not skip_rel(rel):
                        rels.append(rel)
        else:
            rels = walk_md(root, ROOMS["journal"])
        for rel in rels:
            n = read_note(root, rel)
            if n is None:
                continue
            d = date_of(rel, n["front"], ("date", "created"))
            if d is None:
                find("journal_undated", rel.as_posix(),
                     "The journal entry carries no `date` and its filename has "
                     "no date prefix, so it cannot be placed in time.",
                     "Add `date: YYYY-MM-DD`, or rename the file with its date "
                     "in front.")
                continue
            age = (today - d).days
            if age < 0 or age > WINDOW_DAYS:
                continue
            names = []
            for key in ("journal_topics", "journal_projects", "journal_goals",
                        "journal_key_element"):
                names += first_field(n["front"], key)
            if add_events(rel, d, "journal", names, n["prose"]):
                sources_counted["journal"] += 1

    # Scratchpads: the user's raw writing, counted only while unprocessed, so
    # a scratchpad and the journal entries it became are never counted twice.
    if (root / ROOMS["scratchpad"]).is_dir():
        for rel in walk_md(root, ROOMS["scratchpad"]):
            m = DATE_PREFIX.match(rel.stem)
            if not m:
                continue
            d = iso_date(m.group(1))
            if d is None:
                continue
            age = (today - d).days
            if age < 0 or age > WINDOW_DAYS:
                continue
            n = read_note(root, rel)
            if n is None or truthy(n["front"].get("processed", "")):
                continue
            if add_events(rel, d, "scratchpad", [], n["prose"]):
                sources_counted["scratchpad"] += 1
    else:
        degrade("scratchpad", "no folder at %s" % ROOMS["scratchpad"],
                "raw daily writing adds nothing to the attention score")

    # Filed notes: attention, a lighter kind. Frontmatter links only, because
    # a reference note quotes a whole article and its body is not the user's
    # words.
    if (root / ROOMS["notes"]).is_dir():
        for rel in walk_md(root, ROOMS["notes"]):
            n = read_note(root, rel)
            if n is None:
                continue
            if str(n["front"].get("type", "")).strip() not in ("note", ""):
                continue
            d = date_of(rel, n["front"], ("created", "date"))
            if d is None:
                continue
            age = (today - d).days
            if age < 0 or age > WINDOW_DAYS:
                continue
            names = []
            for key in ("note_topics", "note_key_elements", "note_projects"):
                names += first_field(n["front"], key)
            if add_events(rel, d, "notes", names):
                sources_counted["notes"] += 1

    # --- planner items -----------------------------------------------------
    planner_items = []
    planner_linked = 0
    if (root / ROOMS["planner"]).is_dir():
        for rel in walk_md(root, ROOMS["planner"]):
            n = read_note(root, rel)
            if n is None:
                continue
            if str(n["front"].get("type", "")).strip() != "planner-item":
                continue
            planner_items.append((rel, n))
            links = first_field(n["front"], "planner_link")
            if not links:
                continue
            planner_linked += 1
            d = (iso_date(n["front"].get("planned_day", ""))
                 or iso_date(n["front"].get("done_at", ""))
                 or iso_date(n["front"].get("completed_at", "")))
            if d is None:
                continue
            age = (today - d).days
            if 0 <= age <= WINDOW_DAYS and add_events(rel, d, "planner", links):
                sources_counted["planner"] += 1
    else:
        degrade("planner", "no folder at %s" % ROOMS["planner"],
                "no planner activity is counted per project")
    if planner_items and planner_linked == 0:
        degrade("planner_link",
                "no planner item carries %s"
                % " or ".join("`%s`" % f for f in FIELDS["planner_link"]),
                "planner_open_this_week and planner_done_7d are 0 for every "
                "project")

    def attention(rel):
        evs = events.get(rel, [])
        n7 = n14 = n30 = 0
        score = 0
        last = None
        for d, _kind in evs:
            age = (today - d).days
            if age < 0 or age > WINDOW_DAYS:
                continue
            n30 += 1
            if age <= 7:
                n7 += 1
            if age <= 14:
                n14 += 1
            score += weight_for(age)
            if last is None or d > last:
                last = d
        return {"n7": n7, "n14": n14, "n30": n30, "score": score,
                "last_seen": last.isoformat() if last else None}

    def mtime_date(rel):
        try:
            ts = (root / rel).stat().st_mtime
        except OSError:
            return None
        return datetime.date.fromtimestamp(ts).isoformat()

    def days_to(d):
        return (d - today).days if d else None

    # --- the week ----------------------------------------------------------
    iso_y, iso_w, _ = today.isocalendar()
    week_id = "%04d-W%02d" % (iso_y, iso_w)
    week_start = today - datetime.timedelta(days=today.isoweekday() - 1)
    week_end = week_start + datetime.timedelta(days=6)
    week_rel = Path(ROOMS["planner_weeks"]) / ("%s.md" % week_id)
    week_note = read_note(root, week_rel) if (root / week_rel).is_file() else None

    # --- goals -------------------------------------------------------------
    goals_open = []
    goal_status = {}
    for rel, n in entities["goals"].items():
        front = n["front"]
        status = str(front.get("status", "")).strip().strip("\"'").lower()
        goal_status[rel] = status
        if status and status not in OPEN_STATUS["goal"]:
            continue
        target = iso_date(front.get("target_date", ""))
        d2t = days_to(target)
        if status == "active" and d2t is not None and d2t < 0:
            find("goal_overdue_active", rel.as_posix(),
                 "`%s` is still `active` and its target date passed %d day(s) "
                 "ago." % (display_name(rel, front), -d2t),
                 "Move the target date, or set `status` to what is now true.")
        goals_open.append({
            "name": display_name(rel, front),
            "path": rel.as_posix(),
            "status": status or None,
            "key_element": (first_field(front, "goal_key_element") or [None])[0],
            "target_date": target.isoformat() if target else None,
            "days_to_target": d2t,
            "carriers": {
                "projects": [link_name(v) for v in first_field(front, "goal_projects")],
                "habits": [link_name(v) for v in first_field(front, "goal_habits")],
                # Additive within schema 1 (2026-09-15): a third carrier shape.
                # A reader that knows only projects and habits ignores it.
                "workstreams": [link_name(v) for v in first_field(front, "goal_workstreams")],
            },
        })
    goals_open.sort(key=lambda g: (g["target_date"] is None,
                                   g["target_date"] or "", norm(g["name"])))

    # --- projects ----------------------------------------------------------
    focus, active = [], []
    ranks = {}
    for rel, n in entities["projects"].items():
        front = n["front"]
        status = str(front.get("status", "")).strip().strip("\"'").lower()
        raw_rank = str(front.get("focus_rank", "")).strip().strip("\"'")
        rank = None
        if raw_rank.isdigit():
            rank = int(raw_rank)
        target = iso_date(front.get("target_date", ""))
        goal_rel = None
        for v in first_field(front, "project_goal"):
            goal_rel = resolve(link_name(v))
            if goal_rel is not None:
                break
        goal_block = None
        gnames = first_field(front, "project_goal")
        if goal_rel is not None:
            goal_block = {
                "name": display_name(goal_rel, entities["goals"][goal_rel]["front"])
                        if goal_rel in entities["goals"] else goal_rel.stem,
                "status": goal_status.get(goal_rel) or None,
            }
        elif gnames:
            goal_block = {"name": link_name(gnames[0]), "status": None}
        rec = {
            "name": display_name(rel, front),
            "path": rel.as_posix(),
            "focus_rank": rank,
            "status": status or None,
            "goal": goal_block,
            "key_element": (first_field(front, "project_key_element") or [None])[0],
            "planner_open_this_week": 0,
            "planner_done_7d": 0,
            "attention": attention(rel),
            "target_date": target.isoformat() if target else None,
            "days_to_target": days_to(target),
        }
        is_open = (not status) or status in OPEN_STATUS["project"]
        if rank is not None:
            ranks.setdefault(rank, []).append(rel.as_posix())
            focus.append(rec)
            if not is_open:
                find("focus_rank_not_active", rel.as_posix(),
                     "`%s` carries `focus_rank: %d` but its status is `%s`."
                     % (rec["name"], rank, status or "empty"),
                     "Drop the rank, or set the status back to active.")
        if is_open:
            active.append(rec)
    focus.sort(key=lambda p: (p["focus_rank"], norm(p["name"])))
    active.sort(key=lambda p: (
        p["focus_rank"] is None, p["focus_rank"] or 0,
        -p["planner_open_this_week"], -p["attention"]["score"],
        p["target_date"] is None, p["target_date"] or "", norm(p["name"])))
    if len(focus) > THRESHOLDS["focus_max"]:
        find("focus_over_max", None,
             "%d projects carry `focus_rank`; the limit is %d."
             % (len(focus), THRESHOLDS["focus_max"]),
             "Drop a rank in the Properties panel until %d are left."
             % THRESHOLDS["focus_max"])
    for r, paths in sorted(ranks.items()):
        if len(paths) > 1:
            find("focus_duplicate_rank", sorted(paths)[0],
                 "`focus_rank: %d` is on %d projects: %s."
                 % (r, len(paths), ", ".join(sorted(paths))),
                 "Give each project its own rank; the set is 1, 2, 3.")
    if entities["projects"] and not focus:
        degrade("focus_rank",
                "no project carries `focus_rank` yet; the field is in the "
                "guideline, the decision is not made",
                "the focus answer is a proposal, never a stored decision")

    # --- weekly goals and the highlight ------------------------------------
    weekly_items, highlight_rows = [], []
    if week_note is None:
        reason = "no note at %s" % week_rel.as_posix()
        degrade("planner_week", reason,
                "weekly_goals and highlight are empty")
    else:
        reason = None
        weekly_items = parse_checklist(week_note["body"])
        highlight_rows = parse_highlights(week_note["body"])
        if len(weekly_items) > THRESHOLDS["weekly_goals_max"]:
            find("weekly_goals_over_max", week_rel.as_posix(),
                 "%d weekly goals for %s; the limit is %d."
                 % (len(weekly_items), week_id, THRESHOLDS["weekly_goals_max"]),
                 "Move one to next week; the week does not get longer.")

    weekly_goals = {
        "week": week_id,
        "path": week_rel.as_posix() if week_note is not None else None,
        "items": weekly_items,
        "done_count": sum(1 for i in weekly_items if i["done"]),
        "reason": reason,
    }

    today_row = None
    recent = []
    for row in highlight_rows:
        if row["date"] == today.isoformat():
            today_row = row
        elif row["date"] < today.isoformat():
            recent.append(row)
    recent.sort(key=lambda r: r["date"], reverse=True)
    highlight = {
        "date": today.isoformat(),
        "text": today_row["text"] if today_row else None,
        "done": today_row["done"] if today_row else None,
        "path": week_rel.as_posix() if week_note is not None else None,
        "reason": (reason if week_note is None else
                   (None if today_row else
                    "no row for %s in the highlights table" % today.isoformat())),
        "recent": recent[:7],
    }

    # --- key elements ------------------------------------------------------
    open_goal_by_ke, active_project_by_ke = {}, {}
    for g in goals_open:
        if g["key_element"]:
            k = norm(link_name(g["key_element"]))
            open_goal_by_ke[k] = open_goal_by_ke.get(k, 0) + 1
    for p in active:
        if p["key_element"]:
            k = norm(link_name(p["key_element"]))
            active_project_by_ke[k] = active_project_by_ke.get(k, 0) + 1

    key_elements = []
    for rel, n in entities["key_elements"].items():
        front = n["front"]
        status = str(front.get("status", "")).strip().strip("\"'").lower()
        if status and status not in OPEN_STATUS["key_element"]:
            continue
        name = display_name(rel, front)
        keys = {norm(rel.stem), norm(name)}
        key_elements.append({
            "name": name,
            "path": rel.as_posix(),
            "status": status or None,
            "open_goals": sum(open_goal_by_ke.get(k, 0) for k in keys),
            "active_projects": sum(active_project_by_ke.get(k, 0) for k in keys),
            "attention": attention(rel),
            "last_modified": mtime_date(rel),
        })
    key_elements.sort(key=lambda k: (-k["attention"]["score"], norm(k["name"])))

    # --- topics ------------------------------------------------------------
    ranked = []
    for rel, n in entities["topics"].items():
        front = n["front"]
        lifecycle = str(front.get("lifecycle", "")).strip().strip("\"'").lower()
        if lifecycle in ("promoted", "dormant"):
            continue
        att = attention(rel)
        ranked.append({
            "name": display_name(rel, front),
            "path": rel.as_posix(),
            "key_element": (first_field(front, "topic_key_element") or [None])[0],
            "attention": att,
            "last_modified": mtime_date(rel),
        })
    ranked.sort(key=lambda t: (-t["attention"]["score"], -t["attention"]["n7"],
                               norm(t["name"])))
    hot = [t for t in ranked if t["attention"]["score"] > 0][:THRESHOLDS["topics_shown"]]

    # --- today -------------------------------------------------------------
    today_journal, today_scratch = [], []
    jd = root / ROOMS["journal"] / today.strftime("%Y") / today.strftime("%m")
    if jd.is_dir():
        for p in sorted(jd.glob("*.md")):
            if p.is_symlink():
                continue        # Vex F5
            rel = p.relative_to(root)
            if skip_rel(rel):
                continue
            n = read_note(root, rel)
            if n and date_of(rel, n["front"], ("date", "created")) == today:
                today_journal.append(rel.as_posix())
    if (root / ROOMS["scratchpad"]).is_dir():
        for rel in walk_md(root, ROOMS["scratchpad"]):
            m = DATE_PREFIX.match(rel.stem)
            if m and m.group(1) == today.isoformat():
                today_scratch.append(rel.as_posix())

    # Vex F3: validated, bounded, and never read through a symlink. An
    # unparseable VERSION is "unknown" plus a degraded entry, never a
    # verbatim copy of whatever the file happened to hold.
    version = "unknown"
    vf = root / ".icor-for-life/VERSION"
    if vf.is_file() and not vf.is_symlink():
        raw = vf.read_text(encoding="utf-8", errors="ignore")[:64].strip()
        if VERSION_SHAPE.match(raw):
            version = raw
        else:
            degrade("scaffold_version",
                    ".icor-for-life/VERSION does not hold a version string",
                    "scaffold_version is `unknown`")
    elif vf.is_symlink():
        degrade("scaffold_version", ".icor-for-life/VERSION is a symlink",
                "scaffold_version is `unknown`; the file was not read")

    findings.sort(key=lambda f: (f["id"], f["path"] or ""))

    return {
        "schema": SCHEMA,
        "generated_at": datetime.datetime.now(datetime.timezone.utc)
                        .strftime("%Y-%m-%dT%H:%M:%SZ"),
        "generated_local_date": today.isoformat(),
        "scaffold_version": version,
        "week": {
            "iso": week_id,
            "start": week_start.isoformat(),
            "end": week_end.isoformat(),
            "note": week_rel.as_posix() if week_note is not None else None,
        },
        "thresholds": dict(THRESHOLDS),
        "goals": {
            "open": goals_open,
            "achieved_90d": [],
            "order_rule": "target_date ascending, nulls last, then name",
        },
        "projects": {
            "focus": focus,
            "active": active,
            "active_count": len(active),
            "order_rule": "focus_rank asc, planner_open_this_week desc, "
                          "attention.score desc, target_date asc nulls last, name",
        },
        "weekly_goals": weekly_goals,
        "highlight": highlight,
        "key_elements": key_elements,
        "topics": {
            "hot": hot,
            "ranked_count": len(ranked),
            "sources_counted": sources_counted,
            "order_rule": "score desc, n7 desc, name",
        },
        "today": {
            "date": today.isoformat(),
            "journal_entries": today_journal,
            "scratchpads": today_scratch,
        },
        "findings": findings,
        "degraded": degraded,
    }


# --- the two sentinel blocks ------------------------------------------------

def _after_sentinel(body, sentinel):
    i = body.find(sentinel)
    if i == -1:
        return []
    return body[i + len(sentinel):].splitlines()[1:]


def parse_checklist(body):
    """The `## Weekly priorities` checklist. A line that is not a checkbox
    is not a priority: it is left alone and reported by nobody."""
    items = []
    for line in _after_sentinel(body, PRIORITIES_SENTINEL):
        s = line.strip()
        if s.startswith("#"):
            break
        m = CHECKBOX.match(line)
        if m:
            items.append({"text": m.group(2).strip(),
                          "done": m.group(1).lower() == "x"})
        elif s == "" and items:
            break
    return items


def parse_highlights(body):
    """The `## Daily highlights` table: Date | Highlight | Done. `Y` done, `N` not
    done, `_` or blank pending, the marker set the habit log already uses."""
    rows = []
    for line in _after_sentinel(body, HIGHLIGHTS_SENTINEL):
        s = line.strip()
        if s.startswith("#"):
            break
        if not s.startswith("|"):
            if rows:
                break
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if len(cells) < 2:
            continue
        d = iso_date(cells[0])
        if d is None:
            continue        # the header row and the dashes
        marker = (cells[2].strip().upper() if len(cells) > 2 else "")
        done = True if marker == "Y" else (False if marker == "N" else None)
        rows.append({"date": d.isoformat(), "text": cells[1], "done": done})
    return rows


# --- the brief --------------------------------------------------------------

def brief(report, elapsed=None):
    """About twenty lines, rendered here and never by a model."""
    L = []
    fresh = "stale" if is_stale(report) else "fresh"
    stamp = "%s %s" % (report["generated_local_date"],
                       report["generated_at"][11:16])
    L.append("Life snapshot %s UTC (%s)%s"
             % (stamp, fresh,
                "" if elapsed is None else ", %.2fs" % elapsed))

    g = report["goals"]["open"]
    L.append("Goals (%d open): %s"
             % (len(g), join_short([x["name"] for x in g], 6)))

    f = report["projects"]["focus"]
    if f:
        L.append("Focus (your ranks): "
                 + " . ".join("%s %s" % (p["focus_rank"], p["name"]) for p in f))
    else:
        L.append("Focus (your ranks): none set. Say which projects matter and "
                 "I will store the decision.")
    L.append("Active projects: %d (focus set on %d)"
             % (report["projects"]["active_count"], len(f)))

    w = report["weekly_goals"]
    if w["items"]:
        L.append("Weekly priorities %s (%d of %d done): %s"
                 % (w["week"], w["done_count"], len(w["items"]),
                    " . ".join("[%s] %s" % ("x" if i["done"] else " ", i["text"])
                               for i in w["items"])))
    else:
        L.append("Weekly priorities %s: none (%s)" % (w["week"], w["reason"] or "empty"))

    h = report["highlight"]
    if h["text"]:
        state = {True: "done", False: "not done", None: "pending"}[h["done"]]
        L.append("Daily highlight: %s (%s)" % (h["text"], state))
    else:
        L.append("Daily highlight: none recorded (%s)" % (h["reason"] or "empty"))

    ke = report["key_elements"]
    L.append("Key elements (%d): %s"
             % (len(ke), join_short([k["name"] for k in ke], 8)))

    hot = report["topics"]["hot"]
    if hot:
        L.append("Hot topics (%dd, weighted): %s"
                 % (WINDOW_DAYS,
                    " . ".join("%s %d" % (t["name"], t["attention"]["score"])
                               for t in hot)))
    else:
        L.append("Hot topics (%dd, weighted): none scored above 0 (%d topics "
                 "ranked)" % (WINDOW_DAYS, report["topics"]["ranked_count"]))
    sc = report["topics"]["sources_counted"]
    L.append("Attention sources counted: "
             + ", ".join("%s %d" % (k, v) for k, v in sc.items()))

    t = report["today"]
    L.append("Today: %d journal entr%s, %d scratchpad%s"
             % (len(t["journal_entries"]),
                "y" if len(t["journal_entries"]) == 1 else "ies",
                len(t["scratchpads"]),
                "" if len(t["scratchpads"]) == 1 else "s"))

    d = report["degraded"]
    if d:
        L.append("Degraded (%d):" % len(d))
        for e in d:
            L.append("  %s: %s -> %s" % (e["source"], e["reason"], e["effect"]))
    else:
        L.append("Degraded: none")

    fi = report["findings"]
    if fi:
        L.append("Findings (%d):" % len(fi))
        for e in fi[:5]:
            L.append("  %s: %s" % (e["id"], e["message"]))
        if len(fi) > 5:
            L.append("  ... and %d more in snapshot.json" % (len(fi) - 5))
    else:
        L.append("Findings: none")
    return "\n".join(L)


def join_short(names, keep):
    if not names:
        return "none"
    shown = names[:keep]
    tail = "" if len(names) <= keep else ", ... (%d more)" % (len(names) - keep)
    return ", ".join(shown) + tail


# --- main -------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default=None)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--brief", action="store_true")
    a = ap.parse_args()
    root = Path(a.root).resolve() if a.root else DEFAULT_ROOT
    if not root.is_dir():
        sys.exit("FAIL no such folder: %s" % root)
    if not (root / "04 Inner World").is_dir():
        sys.exit("FAIL %s is not a vault root (no '04 Inner World'); "
                 "give the vault root" % root)

    started = time.time()
    report = run(root)
    elapsed = time.time() - started

    payload = json.dumps(report, indent=2, ensure_ascii=False)
    hits = secret_findings(payload)
    if hits:
        sys.exit("FAIL a secret-shaped value reached the snapshot (%s); "
                 "nothing was written. Find it in the note it came from and "
                 "move it to .env." % hits[0])

    if a.write:
        # Vex F2 and F6: the write stays inside the vault's machine layer,
        # whatever is planted on the path. A symlinked `scripts/` folder or
        # a pre-planted `snapshot.json.tmp` symlink used to let this script
        # overwrite any file the user can write. O_NOFOLLOW|O_EXCL on the
        # temp file, a resolve check on the parent, and a symlink check on
        # the destination close all three; the `except` clears the temp so
        # a failed swap leaves nothing behind.
        dest = root / ".icor-for-life/scripts/snapshot.json"
        tmp = dest.with_suffix(".json.tmp")
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            real_parent = dest.parent.resolve()
            if real_parent != root.resolve() / ".icor-for-life" / "scripts":
                sys.exit("FAIL %s resolves outside the vault machine layer; "
                         "nothing was written" % dest.parent)
            # BOTH refusals happen BEFORE the temp file exists. They call
            # sys.exit, which raises SystemExit, which is not an OSError, so
            # the cleanup in the `except` below never ran for them: refusing
            # used to leave a `snapshot.json.tmp` holding the whole payload.
            # Checking first is the fix, not a second except clause.
            if dest.is_symlink():
                sys.exit("FAIL %s is a symlink; nothing was written" % dest)
            if tmp.is_symlink() or tmp.exists():
                tmp.unlink()
            # os.O_NOFOLLOW DOES NOT EXIST ON WINDOWS, and naming it unguarded
            # raised AttributeError before a byte was written: every Windows
            # session start lost its snapshot (Conrad Froehling, 2026-09-16).
            # Where the flag is missing it contributes 0, and the protection it
            # stands for is still there: `dest.is_symlink()` and the
            # `tmp.is_symlink()` unlink above both refuse a planted link before
            # this line runs, and O_EXCL refuses to open anything that already
            # exists, symlink included. What is lost with the flag is only the
            # atomicity of that refusal, on the platform that has no symlinks
            # to plant in the first place without the same privilege this whole
            # report is about.
            fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL
                         | getattr(os, "O_NOFOLLOW", 0), 0o644)
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                fh.write(payload + "\n")
            os.replace(tmp, dest)
        except OSError as exc:
            try:
                tmp.unlink()
            except OSError:
                pass
            sys.exit("FAIL cannot write %s: %s" % (dest, exc))
        if not (a.json or a.brief):
            print("OK wrote %s" % dest.relative_to(root))

    if a.json:
        print(payload)
    if a.brief or not (a.json or a.write):
        print(brief(report, elapsed))
    return 0


if __name__ == "__main__":
    sys.exit(main())
