#!/usr/bin/env python3
"""link-dates-to-daily-notes.py: a full date written in a note body is a
link to that day's daily note (GL-1011).

Why. An empty daily note is worth nothing on its own. The same note with
forty backlinks is the timeline of everything that touched that day, and
the backlinks arrive for free the moment the date is written as a link.
So `2026-09-11` in prose becomes `[[2026-09-11]]`, and the daily note is
created empty if it does not exist yet.

Everything here is deterministic (GL-1005): which spans are prose, which
are data, which dates are real. Nothing in this file decides what a date
MEANS.

Scope follows one principle: the daily note is a timeline of the USER's
life and work, so only the user's own notes link into it. The team's
operating records stay bare, and the daily notes never fill up with the
team's housekeeping.

  IN   the body (after the closing frontmatter ---) of .md files under
       04 Inner World/. Nothing else.
  OUT  all of 06 AI Team/ without exception: session logs, specialist
       journals, Team Knowledge, SOPs, Guidelines, Workstreams, Tasks,
       Templates, Scripts, AI Sessions. Also 00 Daily Scratchpad/ itself,
       01 Inbox/ (captures and their archive), 02 Planner/, 05 Assets/ and
       07 Databases/.
  Inside the two rooms, still OUT: YAML frontmatter (typed dates are
       data, GL-1002); fenced and inline code; anything already inside
       [[...]]; markdown link targets and URLs; blockquotes (a quoted
       passage is someone's words, kept as they were); the `## Original
       Text` section of a journal entry, down to the next heading of the
       same or a higher level; a date that is part of a longer token
       (2026-09-11-slug, tsk-2026-09-09-020, 2026-09-11T14:12,
       2026-09-11.md); any path segment starting with _ (archives,
       snapshots, _files); INDEX.md; .obsidian/; node_modules/.

Hard rule 1 is why 01 Inbox/, blockquotes and Original Text are out: what
the user wrote in a capture or in the Original Text section is never
edited, not even by two pairs of brackets (member report, myPKA 7.0.1 /
ICOR for Life 2.2.1, item 1).

The second half of that matters as much as the first. About 114k raw
YYYY-MM-DD strings live in a lived-in vault and almost none of them are
prose, so a rule that is not narrow is vandalism.

A date is only linked when `[[YYYY-MM-DD]]` can actually resolve to the
daily note, which means: the daily-note format's last segment is
YYYY-MM-DD, and no OTHER note in the vault is named YYYY-MM-DD.md. A
second file with that name makes the wikilink ambiguous, so that date is
reported as a collision and left alone.

Usage:
  link-dates-to-daily-notes.py [<vault-root>] [--check|--dry-run|--fix]
                               [--path FILE-OR-FOLDER]... [--since YYYY-MM-DD]
                               [--json]

Exit codes: 0 clean | 1 unlinked mentions found (--check) | 2 cannot run
"""
import argparse, datetime, importlib.util, json, os, re, sys
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

# A date delimited by anything that is not a word character, a hyphen or a
# slash, and not followed by a file extension. The three exclusions are the
# three shapes that look like a date and are not prose: a slug
# (2026-09-11-jeff-meyers), an ISO timestamp or id (2026-09-11T14:12,
# tsk-2026-09-09-020) and a path or filename (Journal/2026/09, 2026-09-11.md).
DATE = re.compile(r"(?<![\w\-/])(\d{4})-(\d{2})-(\d{2})(?![\w\-/])(?!\.\w)")

# The alias separator is `|` in prose and `\|` inside a markdown table, where
# a raw pipe would end the cell. Both are the same link to Obsidian, so both
# count as already linked; reading only the bare pipe made a dated table row
# invisible to the existence check below, which is the whole point of the
# function (Steven Koegler, 2026-09-01).
DAILY_LINK = re.compile(r"\[\[(\d{4}-\d{2}-\d{2})(?:\\?\|[^\]\n]*)?\]\]")

FRONTMATTER = re.compile(r"^---\r?\n.*?^(?:---|\.\.\.)[ \t]*\r?\n", re.S | re.M)
INLINE_CODE = re.compile(r"`[^`\n]*`")
FENCE = re.compile(r"[ \t]{0,3}(`{3,}|~{3,})")
HEADING = re.compile(r"[ \t]{0,3}(#{1,6})[ \t]+(.*?)[ \t#]*\r?\n?$")
BLOCKQUOTE = re.compile(r"[ \t]{0,3}>")
# The journal section that hard rule 1 protects (GL-1003). Matched on the
# heading's words, any level, any case, so `### original text` in an older
# entry is protected too.
PROTECTED_HEADING = "original text"
WIKILINK = re.compile(r"!?\[\[[^\]\n]*\]\]")
MD_LINK = re.compile(r"!?\[[^\]\n]*\]\([^)\n]*\)")
LINK_TARGET = re.compile(r"\]\([^)\n]*\)")
URL = re.compile(r"(?:https?://|www\.)\S+")

# The rooms the user writes in and the script may write to. The daily note
# is a timeline of the user's life and work, so this list IS the rule, not
# an optimisation of it: 06 AI Team/ is the team's operating record and
# never links in. 01 Inbox/ is the user's too, but every file in it is a
# capture or an archived capture, and hard rule 1 says a capture is never
# edited, so the inbox is out (2.3.0). A capture's dates get their links
# when it is processed into a note in this room. 3.0 has no 03 WiP: one a
# migrated folder still holds is nobody's room and stays bare.
USER_ROOMS = ("04 Inner World",)
# Folders that are never prose, wherever they sit inside those rooms.
EXCLUDED_SEGMENTS = {".obsidian", ".git", ".trash", "node_modules",
                     "__pycache__", "Templates"}
# Walking these answers nothing and costs everything.
PRUNE = {".obsidian", ".git", ".trash", "node_modules", "__pycache__"}
EXCLUDED_NAMES = {"index.md"}

OBSIDIAN_DEFAULT = {"folder": "", "format": "YYYY-MM-DD"}


def fail(msg):
    print("FAIL " + msg, file=sys.stderr)
    sys.exit(2)


# --- the daily-note contract ----------------------------------------------

def read_daily_config(root: Path, allow_default: bool):
    """Read .obsidian/daily-notes.json. Never hardcode the folder: a member
    may have moved it, and a script that assumes the path writes into the
    wrong room silently."""
    cfg_file = root / ".obsidian" / "daily-notes.json"
    if not cfg_file.is_file():
        if not allow_default:
            fail(f"no {cfg_file.relative_to(root)}; cannot know where daily "
                 f"notes live, and guessing would write into the wrong room")
        print(f"WARNING no .obsidian/daily-notes.json; falling back to "
              f"Obsidian's defaults (folder '', format YYYY-MM-DD)",
              file=sys.stderr)
        return dict(OBSIDIAN_DEFAULT), True
    try:
        cfg = json.loads(cfg_file.read_text(encoding="utf-8"))
    except ValueError as e:
        fail(f".obsidian/daily-notes.json is not valid JSON: {e}")
    cfg = {"folder": cfg.get("folder", ""),
           "format": cfg.get("format") or OBSIDIAN_DEFAULT["format"]}
    return cfg, False


def render_format(cfg, d: datetime.date) -> str:
    return (cfg["format"].replace("YYYY", f"{d.year:04d}")
                         .replace("MM", f"{d.month:02d}")
                         .replace("DD", f"{d.day:02d}"))


def daily_note_path(root: Path, cfg, d: datetime.date) -> Path:
    rel = render_format(cfg, d)
    folder = (cfg.get("folder") or "").strip("/")
    return root / folder / (rel + ".md") if folder else root / (rel + ".md")


def check_format(cfg):
    """`[[YYYY-MM-DD]]` only resolves if the note is NAMED YYYY-MM-DD. Any
    other format makes every link this script writes point at nothing, so
    refuse rather than produce 3000 dangling links."""
    last = cfg["format"].replace("\\", "/").split("/")[-1]
    if last != "YYYY-MM-DD":
        fail(f"daily-note format ends in '{last}', not 'YYYY-MM-DD'; a "
             f"[[YYYY-MM-DD]] link could not resolve to it")
    probe = render_format(cfg, datetime.date(2026, 1, 2))
    if re.search(r"[A-Za-z]", probe):
        fail(f"daily-note format '{cfg['format']}' uses tokens this script "
             f"does not understand; only YYYY, MM and DD are supported")


# --- scope -----------------------------------------------------------------

def in_scope(rel: Path) -> bool:
    parts = rel.parts
    if not parts or not rel.name.lower().endswith(".md"):
        return False
    if rel.name.lower() in EXCLUDED_NAMES or rel.name.startswith("_"):
        return False
    if parts[0] not in USER_ROOMS:
        return False
    for seg in parts[:-1]:
        if seg.startswith("_") or seg in EXCLUDED_SEGMENTS:
            return False
    return True


def walk(root: Path):
    """One walk answers both questions: which files are in scope, and which
    notes are named YYYY-MM-DD.md anywhere in the vault."""
    scoped, named = [], {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in PRUNE]
        here = Path(dirpath)
        for name in filenames:
            if not name.lower().endswith(".md"):
                continue
            rel = (here / name).relative_to(root)
            stem = name[:-3]
            if DATE.fullmatch(stem):
                named.setdefault(stem, []).append(rel)
            if in_scope(rel):
                scoped.append(rel)
    return sorted(scoped), named


def collisions(root, cfg, named):
    """A date whose name is taken by a note that is NOT its daily note. The
    wikilink would be ambiguous, so the date is reported and never linked."""
    bad = {}
    for stem, rels in named.items():
        try:
            d = datetime.date.fromisoformat(stem)
        except ValueError:
            continue
        want = daily_note_path(root, cfg, d).relative_to(root)
        others = [r for r in rels if r != want]
        if others:
            bad[stem] = sorted(str(o) for o in others)
    return bad


# --- reading one file ------------------------------------------------------

def body_offset(text: str) -> int:
    if not text.startswith("---"):
        return 0
    m = FRONTMATTER.match(text)
    return m.end() if m else len(text)


def masked(body: str) -> bytearray:
    """Mark every span that is not prose, or is prose the script may not
    edit. Cheap, and the only thing standing between this script and
    rewriting a code sample, a quotation or the user's Original Text."""
    mask = bytearray(len(body))

    def mark(lo, hi):
        for i in range(lo, hi):
            mask[i] = 1

    pos, open_at, fence = 0, None, None
    protected_at, protected_level = None, None
    in_quote = False
    for line in body.splitlines(keepends=True):
        end = pos + len(line)
        m = FENCE.match(line)
        if m:
            mark_char = m.group(1)[0]
            if open_at is None:
                open_at, fence = pos, mark_char
            elif mark_char == fence:
                mark(open_at, end)
                open_at, fence = None, None
            in_quote = False
            pos = end
            continue
        if open_at is None:
            # A heading inside a code fence is code, so only headings
            # outside one open or close the protected section.
            h = HEADING.match(line)
            if h:
                level = len(h.group(1))
                if protected_at is not None and level <= protected_level:
                    mark(protected_at, pos)
                    protected_at, protected_level = None, None
                if (protected_at is None
                        and h.group(2).strip().lower() == PROTECTED_HEADING):
                    protected_at, protected_level = pos, level
            # A blockquote runs from its first `>` line to the next blank
            # line. A line after a `>` line with no `>` of its own is still
            # the quote (markdown's lazy continuation), so it is kept too.
            if BLOCKQUOTE.match(line):
                in_quote = True
            elif not line.strip():
                in_quote = False
            if in_quote:
                mark(pos, end)
        pos = end
    if open_at is not None:          # unclosed fence: treat the rest as code
        mark(open_at, len(body))
    if protected_at is not None:     # Original Text runs to the end of the note
        mark(protected_at, len(body))

    for rx in (INLINE_CODE, WIKILINK, MD_LINK, LINK_TARGET, URL):
        for m in rx.finditer(body):
            mark(*m.span())
    return mask


def mentions(text: str, since):
    """Every bare, real, prose date in the body, as (start, end, date)."""
    start = body_offset(text)
    body = text[start:]
    mask = masked(body)
    out = []
    for m in DATE.finditer(body):
        if mask[m.start()]:
            continue
        try:
            d = datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            continue                 # 2026-13-45 is not a date
        if since and d < since:
            continue
        out.append((start + m.start(), start + m.end(), d))
    return out


def already_linked(text: str, since):
    """Dates that ALREADY point at a daily note. They need no rewrite, but
    the note behind them still has to exist: a link is only worth writing
    while it lands somewhere, and a member may have typed [[2026-09-11]] by
    hand or deleted the note afterwards."""
    body = text[body_offset(text):]
    out = set()
    for m in DAILY_LINK.finditer(body):
        try:
            d = datetime.date.fromisoformat(m.group(1))
        except ValueError:
            continue
        if not since or d >= since:
            out.add(d)
    return out


def line_of(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


# --- main ------------------------------------------------------------------

ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
ap.add_argument("root", nargs="?", default=None)
mode = ap.add_mutually_exclusive_group()
mode.add_argument("--check", action="store_true", help="list unlinked mentions, exit 1 if any (default)")
mode.add_argument("--dry-run", action="store_true", help="what --fix would do, no writes")
mode.add_argument("--fix", action="store_true", help="write the links and create the missing daily notes")
ap.add_argument("--since", default=None, help="only mentions of dates on or after this day, YYYY-MM-DD")
# One note, or a folder, instead of the whole vault. SOP-1001 processes one
# scratchpad and then wants the dates in THAT note linked; without this, --fix
# rewrote date mentions across every note in the vault as a side effect of
# processing one (Brian Carroll, T16-11). Repeatable; a file is a work list of
# one. The collision scan still walks the whole vault, because a name clash
# anywhere is what makes a link ambiguous here.
ap.add_argument("--path", action="append", default=[], metavar="PATH",
                help="limit the work to this file or folder inside the vault; repeatable")
ap.add_argument("--json", action="store_true")
a = ap.parse_args()

ROOT = Path(a.root).resolve() if a.root else Path(__file__).resolve().parents[2]
if not ROOT.is_dir():
    fail(f"{ROOT} is not a folder")
MODE = "fix" if a.fix else "dry-run" if a.dry_run else "check"
try:
    SINCE = datetime.date.fromisoformat(a.since) if a.since else None
except ValueError:
    fail(f"--since {a.since} is not a YYYY-MM-DD date")

CFG, DEFAULTED = read_daily_config(ROOT, allow_default=(MODE == "check"))
check_format(CFG)

files, named = walk(ROOT)
COLLIDING = collisions(ROOT, CFG, named)

if a.path:
    wanted = []
    for raw in a.path:
        target = Path(raw)
        if not target.is_absolute():
            target = (ROOT / raw) if (ROOT / raw).exists() else target
        target = target.resolve()
        if not target.exists():
            fail(f"--path does not exist: {raw}")
        try:
            rel = target.relative_to(ROOT)
        except ValueError:
            fail(f"--path is outside {ROOT}: {raw}")
        wanted.append(rel)
    scoped = [f for f in files
              if any(f == w or w in f.parents for w in wanted)]
    skipped = [str(w) for w in wanted
               if not any(f == w or w in f.parents for f in files)]
    if skipped:
        # Said out loud rather than passed over: a path that is simply out of
        # the linker's scope (all of 06 AI Team/, 00 Daily Scratchpad/ itself,
        # 01 Inbox/, whose captures hard rule 1 protects) would otherwise look
        # like a clean run on a note nobody looked at.
        print("NOTE out of the linker's scope, nothing to do there: "
              + ", ".join(sorted(skipped)), file=sys.stderr)
    files = scoped

items, per_file, wanted_days = [], {}, set()
for rel in files:
    path = ROOT / rel
    try:
        # From bytes: text mode folds a member's CRLF and any stray CR into
        # LF on the way in, and the write below would then land that folded
        # text as the new file (Ian Slattery, T15-A).
        text, _eol = noteio.read_note(path)
    except (UnicodeDecodeError, OSError):
        continue
    wanted_days |= {d for d in already_linked(text, SINCE)
                    if d.isoformat() not in COLLIDING}
    found = [(s, e, d) for (s, e, d) in mentions(text, SINCE)
             if d.isoformat() not in COLLIDING]
    if not found:
        continue
    per_file[rel] = (text, found)
    for s, _e, d in found:
        items.append({"file": str(rel), "line": line_of(text, s),
                      "date": d.isoformat()})
        wanted_days.add(d)

missing_days = sorted(d for d in wanted_days
                      if not daily_note_path(ROOT, CFG, d).is_file())

changed, created = 0, 0
if MODE == "fix":
    for rel, (text, found) in sorted(per_file.items()):
        out = text
        for s, e, d in reversed(found):          # back to front keeps offsets
            out = out[:s] + "[[" + out[s:e] + "]]" + out[e:]
        # Bytes in, bytes out: the only edit on disk is the two pairs of
        # brackets this script put there.
        noteio.write_note(ROOT / rel, out)
        changed += 1
    for d in missing_days:
        p = daily_note_path(ROOT, CFG, d)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.touch()                                # blank on purpose (GL-1007)
        created += 1
else:
    changed, created = len(per_file), len(missing_days)

report = {
    "root": str(ROOT),
    "mode": MODE,
    "since": a.since,
    "daily_folder": CFG.get("folder", ""),
    "daily_format": CFG["format"],
    "daily_config_defaulted": DEFAULTED,
    "paths": [str(x) for x in a.path],
    "files_scanned": len(files),
    "files_changed": changed,
    "mentions": len(items),
    "daily_notes_created": created,
    "collisions": COLLIDING,
    "items": items,
}

if a.json:
    print(json.dumps(report, indent=2))
else:
    verb = {"fix": ("changed", "linked", "created"),
            "dry-run": ("to change", "to link", "to create"),
            "check": ("with mentions", "unlinked", "missing")}[MODE]
    print(f"link-dates-to-daily-notes: {MODE}"
          + (f"  (since {a.since})" if a.since else ""))
    print(f"  files scanned      : {len(files)}")
    print(f"  files {verb[0]:<13}: {changed}")
    print(f"  mentions {verb[1]:<10}: {len(items)}")
    print(f"  daily notes {verb[2]:<7}: {created}")
    if COLLIDING:
        print(f"  collisions         : {len(COLLIDING)} "
              f"(a note other than the daily note owns this name)")
        for stem in sorted(COLLIDING):
            for other in COLLIDING[stem]:
                print(f"    {stem}  <-  {other}")
    if MODE == "check":
        for it in items:
            print(f"    {it['file']}:{it['line']}  {it['date']}")

if MODE == "check":
    if items:
        print(f"FAIL {len(items)} date mention(s) in scope are not linked to "
              f"their daily note; run --fix", file=sys.stderr)
        sys.exit(1)
    # Under --json, stdout is the JSON document and nothing else. It used to
    # carry this line too, so every caller's json.loads raised on a CLEAN
    # vault and read the count as "no answer" forever, which is the one state
    # that looks like a normal state (pilot A finding F7, pilot B F3).
    print("OK every date mention in scope links to its daily note",
          file=sys.stderr if a.json else sys.stdout)
sys.exit(0)
