#!/usr/bin/env python3
"""Create and edit the week note: weekly priorities and the daily highlight.

Usage:
  planner-week.py ensure            [--week YYYY-Www] [--root R]
  planner-week.py add-priority  "<text>"          [--week] [--root]
  planner-week.py done-priority "<text>"          [--week] [--root] [--undo]
  planner-week.py set-highlight "<text>"  [--date YYYY-MM-DD] [--week] [--root]
  planner-week.py mark-highlight Y|N|_    [--date YYYY-MM-DD] [--week] [--root]
  planner-week.py show              [--week] [--root]

One note per ISO week at `02 Planner/Weeks/YYYY-Www.md`, `type: planner-week`,
per GL-1002 "Planner weeks: weekly priorities and the daily highlight".
The concept lives in the guideline; this file is only the deterministic
writer, because filing is code's job and judgement is not (GL-1005).

What it will not do:
  - it never picks a highlight and never proposes a priority. A model may
    offer a sentence in chat; only the member's confirmed words reach the
    table, and they reach it through this script.
  - it never rewrites a line it did not come to change. A plain line under
    the checklist sentinel is not a priority, and it survives every write
    untouched.
  - it never overwrites an existing note. `ensure` on a note that exists
    says so and changes nothing.
  - it never translates a line ending. A CRLF note stays a CRLF note, byte
    for byte, which is what noteio-icor.py is for.

Exit 0 = the note is in the state the command asked for (including "it
already was"). Exit 1 = refused, with the reason and the next action.
"""
import argparse
import datetime
import importlib.util
import re
import sys
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
DEFAULT_ROOT = HERE.parents[1]

WEEKS_DIR = "02 Planner/Weeks"

PRIORITIES_HEADING = "## Weekly priorities"
PRIORITIES_SENTINEL = "<!-- weekly-priorities: schema=checklist -->"
HIGHLIGHTS_HEADING = "## Daily highlights"
HIGHLIGHTS_SENTINEL = "<!-- daily-highlights: schema=highlight -->"
HIGHLIGHT_HEADER = "| Date | Highlight | Done |"
HIGHLIGHT_RULE = "|---|---|---|"

# The marker set the habit log already defines. One vocabulary, not two.
MARKERS = {"Y": "done", "N": "not done", "_": "pending"}

ISO_WEEK = re.compile(r"^\d{4}-W\d{2}$")
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
CHECKBOX = re.compile(r"^(\s*-\s*\[)([ xX])(\]\s*)(.*\S)\s*$")

# The secret shapes, IDENTICAL to the tuple in life-snapshot.py, which
# lifted it verbatim from `_SECRET_PATTERNS` in write-guard.py so no two
# of the three can disagree about what a secret is (Vex F1, 2026-09-15).
# test-life-snapshot.py asserts the three lists match; when the guard's
# list moves, all three move in the same change.
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


# noteio-icor.py sits beside this script in the public Scaffold and is loaded
# by path, not by name, so the import needs nothing on sys.path. Where it
# does NOT (the private vault, whose Scripts/ folder predates it) the
# identical fallback below runs, the same shape life-snapshot.py uses for
# check-quality.py's readers. The fixture suite asserts the two agree.
def _load_noteio():
    path = HERE / "noteio-icor.py"
    if not path.is_file():
        return None
    try:
        spec = importlib.util.spec_from_file_location("noteio", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        for name in ("FM_CLOSE", "read_note", "write_note", "detect_eol"):
            if not hasattr(mod, name):
                return None
        return mod
    except Exception:
        return None


class _NoteIOFallback:
    """Byte-faithful read and write. Python's text mode is
    universal-newlines on the way in, so the ordinary read-edit-write
    shape silently rewrites the line endings of every note it touches.
    Nothing here translates anything."""
    FM_CLOSE = re.compile(r"\n---\r?\n")

    @staticmethod
    def detect_eol(data):
        crlf = data.count(b"\r\n")
        lf = data.count(b"\n") - crlf
        cr = data.count(b"\r") - crlf
        best = max((crlf, "\r\n"), (lf, "\n"), (cr, "\r"), key=lambda t: t[0])
        return best[1] if best[0] else "\n"

    @classmethod
    def read_note(cls, path):
        data = Path(path).read_bytes()
        return data.decode("utf-8"), cls.detect_eol(data)

    @staticmethod
    def write_note(path, text):
        Path(path).write_bytes(text.encode("utf-8"))


noteio = _load_noteio() or _NoteIOFallback


# --- weeks and dates --------------------------------------------------------

def week_of(d):
    """The ISO week a date falls in, as `YYYY-Www`. ISO, not calendar:
    the 1st of January can belong to last year's week 52 and the note
    name has to say so honestly."""
    y, w, _ = d.isocalendar()
    return "%04d-W%02d" % (y, w)


def week_bounds(week):
    y, w = int(week[:4]), int(week[6:])
    monday = datetime.date.fromisocalendar(y, w, 1)
    return monday, monday + datetime.timedelta(days=6)


def note_path(root, week):
    return Path(root) / WEEKS_DIR / ("%s.md" % week)


def scan(value, what):
    for _name, rx in SECRET_SHAPES:
        if rx.search(value):
            sys.exit("FAIL that %s is secret-shaped; nothing was written. "
                     "A week note is read by the AI team and by anything "
                     "that syncs the vault." % what)


# --- the body -------------------------------------------------------------

def lines_of(text):
    return text.splitlines(keepends=True)


def bare(line):
    return line.rstrip("\r\n")


def sentinel_at(lines, sentinel):
    for i, line in enumerate(lines):
        if bare(line).strip() == sentinel:
            return i
    return -1


def block_end(lines, start):
    """Where the block that begins after `start` stops: the next heading,
    or the end of the file. A blank line does NOT end it, because a member
    who leaves a gap between two priorities still has two priorities."""
    i = start + 1
    while i < len(lines) and not bare(lines[i]).startswith("#"):
        i += 1
    return i


def render_new(week, now):
    monday, sunday = week_bounds(week)
    L = [
        "---",
        "type: planner-week",
        "week: %s" % week,
        "created_at: %s" % now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "tags: []",
        "---",
        "",
        "# %s" % week,
        "",
        "%s to %s." % (monday.isoformat(), sunday.isoformat()),
        "",
        PRIORITIES_HEADING,
        PRIORITIES_SENTINEL,
        "",
        HIGHLIGHTS_HEADING,
        HIGHLIGHTS_SENTINEL,
        HIGHLIGHT_HEADER,
        HIGHLIGHT_RULE,
        "",
    ]
    # A file created from scratch has no line endings of its own to
    # honour, and LF is what the rest of the scaffold ships.
    return "\n".join(L)


def ensure(root, week, quiet=False):
    p = note_path(root, week)
    if p.exists():
        if not quiet:
            print("OK exists, unchanged -> %s" % p)
        return p, False
    if not ISO_WEEK.match(week):
        sys.exit("FAIL %r is not an ISO week (YYYY-Www)" % week)
    p.parent.mkdir(parents=True, exist_ok=True)
    # `utcnow()` is deprecated from 3.12 and removed in a later 3.x: it
    # returns a naive value that CLAIMS to be UTC, which is the whole bug
    # class. `datetime.UTC` would read better and is 3.11+, and this file
    # still runs on the 3.9 that ships with macOS. The rendered bytes are
    # identical: `created_at` is written with an explicit literal Z
    # (render_new), not with an offset (Brian Carroll, B2-6).
    noteio.write_note(p, render_new(
        week, datetime.datetime.now(datetime.timezone.utc)))
    print("OK created -> %s" % p)
    return p, True


def load(root, week):
    p, _ = ensure(root, week, quiet=True)
    text, eol = noteio.read_note(p)
    return p, text, eol


def repair_sections(lines, eol):
    """A note that lost a section (hand-edited, or written before this
    script existed) gets it back rather than a traceback. Appends only;
    nothing above is moved."""
    changed = False
    if sentinel_at(lines, PRIORITIES_SENTINEL) == -1:
        if lines and not lines[-1].endswith(("\n", "\r")):
            lines[-1] += eol
        lines += [PRIORITIES_HEADING + eol, PRIORITIES_SENTINEL + eol, eol]
        changed = True
    if sentinel_at(lines, HIGHLIGHTS_SENTINEL) == -1:
        if lines and not lines[-1].endswith(("\n", "\r")):
            lines[-1] += eol
        lines += [HIGHLIGHTS_HEADING + eol, HIGHLIGHTS_SENTINEL + eol,
                  HIGHLIGHT_HEADER + eol, HIGHLIGHT_RULE + eol, eol]
        changed = True
    return changed


# --- priorities ------------------------------------------------------------

def read_priorities(lines):
    s = sentinel_at(lines, PRIORITIES_SENTINEL)
    if s == -1:
        return []
    out = []
    for i in range(s + 1, block_end(lines, s)):
        m = CHECKBOX.match(bare(lines[i]))
        if m:
            out.append((i, m.group(4).strip(), m.group(2).lower() == "x"))
    return out


def add_priority(root, week, text):
    scan(text, "priority")
    p, raw, eol = load(root, week)
    lines = lines_of(raw)
    repair_sections(lines, eol)
    for _, t, _done in read_priorities(lines):
        if t.strip().lower() == text.strip().lower():
            print("OK already a priority for %s: %s" % (week, t))
            return 0
    s = sentinel_at(lines, PRIORITIES_SENTINEL)
    existing = read_priorities(lines)
    # After the last checkbox if there is one, else directly after the
    # sentinel. Never at the top: order is the member's.
    at = (existing[-1][0] + 1) if existing else (s + 1)
    lines.insert(at, "- [ ] %s%s" % (text.strip(), eol))
    noteio.write_note(p, "".join(lines))
    print("OK priority added to %s: %s" % (week, text.strip()))
    return 0


def done_priority(root, week, text, undo=False):
    p, raw, eol = load(root, week)
    lines = lines_of(raw)
    needle = text.strip().lower()
    hits = [(i, t, d) for i, t, d in read_priorities(lines)
            if needle == t.strip().lower() or needle in t.strip().lower()]
    if not hits:
        sys.exit("FAIL no priority in %s matches %r. Run `planner-week.py "
                 "show` to see the list." % (week, text))
    if len(hits) > 1:
        sys.exit("FAIL %r matches %d priorities in %s; give more of the "
                 "line so exactly one matches." % (text, len(hits), week))
    i, t, done = hits[0]
    want = "" if undo else "x"
    if (done and not undo) or (not done and undo):
        print("OK already %s in %s: %s"
              % ("open" if undo else "done", week, t))
        return 0
    m = CHECKBOX.match(bare(lines[i]))
    tail = lines[i][len(bare(lines[i])):]
    lines[i] = "%s%s%s%s%s" % (m.group(1), want, m.group(3), m.group(4), tail)
    noteio.write_note(p, "".join(lines))
    print("OK %s in %s: %s" % ("reopened" if undo else "done", week, t))
    return 0


# --- highlights ------------------------------------------------------------

def highlight_rows(lines):
    s = sentinel_at(lines, HIGHLIGHTS_SENTINEL)
    if s == -1:
        return -1, []
    rows = []
    for i in range(s + 1, block_end(lines, s)):
        b = bare(lines[i]).strip()
        if not b.startswith("|"):
            continue
        cells = [c.strip() for c in b.strip("|").split("|")]
        if not cells or not ISO_DATE.match(cells[0]):
            continue                       # the header row and the rule
        rows.append((i, cells))
    return s, rows


def insert_at(lines, s, date, rows):
    """Newest on top, whatever order the rows were written in. A day added
    late lands above the days it is newer than and below the ones it is
    not, so the table reads as a log rather than as a write history."""
    for i, cells in rows:
        if cells[0] < date:
            return i
    if rows:
        return rows[-1][0] + 1
    end = block_end(lines, s)
    for i in range(s + 1, end):
        b = bare(lines[i]).strip()
        if b.startswith("|") and "-" in b and set(b) <= set("|-: "):
            return i + 1        # directly under the header rule
    return s + 1


def write_row(lines, i, date, text, marker, eol):
    lines[i] = "| %s | %s | %s |%s" % (date, text, marker, eol)


def set_highlight(root, week, date, text):
    scan(text, "highlight")
    p, raw, eol = load(root, week)
    lines = lines_of(raw)
    repair_sections(lines, eol)
    monday, sunday = week_bounds(week)
    d = datetime.date.fromisoformat(date)
    if not (monday <= d <= sunday):
        sys.exit("FAIL %s is not inside %s (%s to %s). Pass --week for the "
                 "week that day belongs to." % (date, week, monday, sunday))
    s, rows = highlight_rows(lines)
    for i, cells in rows:
        if cells[0] == date:
            marker = cells[2] if len(cells) > 2 and cells[2] else "_"
            write_row(lines, i, date, text.strip(), marker, eol)
            noteio.write_note(p, "".join(lines))
            print("OK highlight replaced for %s: %s" % (date, text.strip()))
            return 0
    lines.insert(insert_at(lines, s, date, rows), "| %s | %s | _ |%s"
                 % (date, text.strip(), eol))
    noteio.write_note(p, "".join(lines))
    print("OK highlight set for %s: %s" % (date, text.strip()))
    return 0


def mark_highlight(root, week, date, marker):
    marker = marker.strip().upper() if marker.strip() != "_" else "_"
    if marker not in MARKERS:
        sys.exit("FAIL marker must be Y, N or _ (%s)"
                 % ", ".join("%s = %s" % kv for kv in MARKERS.items()))
    p, raw, eol = load(root, week)
    lines = lines_of(raw)
    _s, rows = highlight_rows(lines)
    for i, cells in rows:
        if cells[0] == date:
            write_row(lines, i, date, cells[1], marker, eol)
            noteio.write_note(p, "".join(lines))
            print("OK %s marked %s (%s)" % (date, marker, MARKERS[marker]))
            return 0
    sys.exit("FAIL no highlight row for %s in %s. Set the sentence first: "
             "planner-week.py set-highlight --date %s \"...\"" % (date, week, date))


def show(root, week):
    p, raw, _eol = load(root, week)
    lines = lines_of(raw)
    monday, sunday = week_bounds(week)
    print("%s (%s to %s) -> %s" % (week, monday, sunday, p))
    pr = read_priorities(lines)
    if pr:
        for _i, t, done in pr:
            print("  [%s] %s" % ("x" if done else " ", t))
    else:
        print("  no priorities yet")
    _s, rows = highlight_rows(lines)
    if rows:
        for _i, cells in rows:
            print("  %s  %s  %s" % (cells[0], cells[1],
                                    cells[2] if len(cells) > 2 else ""))
    else:
        print("  no highlights yet")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=["ensure", "add-priority",
                                        "done-priority", "set-highlight",
                                        "mark-highlight", "show"])
    ap.add_argument("text", nargs="?")
    ap.add_argument("--week", default=None)
    ap.add_argument("--date", default=None)
    ap.add_argument("--root", default=None)
    ap.add_argument("--undo", action="store_true")
    a = ap.parse_args()

    root = Path(a.root).resolve() if a.root else DEFAULT_ROOT
    if not (root / "04 Inner World").is_dir():
        sys.exit("FAIL %s is not a scaffold root (no `04 Inner World`)" % root)

    today = datetime.date.today()
    date = a.date or today.isoformat()
    if not ISO_DATE.match(date):
        sys.exit("FAIL --date must be YYYY-MM-DD; got %r" % a.date)
    week = a.week or week_of(datetime.date.fromisoformat(date))
    if not ISO_WEEK.match(week):
        sys.exit("FAIL --week must be YYYY-Www; got %r" % a.week)

    if a.command == "ensure":
        ensure(root, week)
        return 0
    if a.command == "show":
        return show(root, week)
    if a.text is None:
        sys.exit("FAIL %s needs its text argument" % a.command)
    if a.command == "add-priority":
        return add_priority(root, week, a.text)
    if a.command == "done-priority":
        return done_priority(root, week, a.text, undo=a.undo)
    if a.command == "set-highlight":
        return set_highlight(root, week, date, a.text)
    if a.command == "mark-highlight":
        return mark_highlight(root, week, date, a.text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
