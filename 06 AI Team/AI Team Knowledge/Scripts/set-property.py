#!/usr/bin/env python3
"""Set (or remove) ONE frontmatter property on ONE note, without rewriting
a byte the caller never meant to touch.

Usage:
  set-property.py <note> <field> <value>
  set-property.py <note> <field> --unset
  set-property.py <note> --show

  <note>   a path, absolute or relative to the working directory
  --root   the scaffold root, when the note path is given relative to it
  --dry    print what would change, write nothing

Why this exists. `focus_rank` on a project is a DECISION, stored as data.
"Focus on these three projects" has to become three frontmatter values
deterministically, and a model editing YAML by hand is the wrong tool for
a deterministic job: it reflows quotes, it normalises line endings, it
reorders keys, and none of that is visible in the diff a member reads.
This does the one thing, reads and writes through noteio-icor.py so the file's
line endings survive byte for byte, and refuses anything it cannot prove
is legal.

Three guards, in order:
  1. The value must be inside the field's closed set, where the field has
     one. `focus_rank` is 1, 2 or 3 and nothing else.
  2. Where GL-1002's per-type table is readable (the public Scaffold, via
     new-base.py's parser), the field must be declared for this note's
     `type`, and a declared enum must hold the value. A field nobody put
     in the guideline is an invented field, and the guideline comes first.
  3. Frontmatter must already exist and parse. This never creates a note
     and never invents a `type`.

Exit 0 = written, or already had that value. Exit 1 = refused, and the
line says which guard refused and what to do instead.
"""
import argparse
import importlib.util
import json
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

# noteio-icor.py sits beside this script in the public Scaffold and is loaded
# by path, not by name, so the import needs nothing on sys.path. Where it
# does NOT sit beside this script (the private vault, whose Scripts/
# folder predates it) the identical fallback below runs, the same shape
# life-snapshot.py uses for check-quality.py's readers. One reader, two
# homes, never two behaviours: the fixture suite asserts they agree.
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

# A frontmatter value that is one wikilink goes in as a double-quoted string.
# Bare, `[[X]]` is a list holding a list, not a link, and Obsidian's Properties
# panel shows it as such. Only a WHOLE value that is a wikilink is quoted; every
# other value is written byte for byte. JSON is used because a JSON string is a
# valid YAML double-quoted scalar, escapes and all.
# new-entity.py carries the same four lines and the fixture suite
# (test-note-scripts.py) asserts the two agree. It cannot live in
# noteio-icor.py: that file is a pinned byte-identical copy of myPKA's noteio.py.
WHOLE_WIKILINK = re.compile(r"^!?\[\[.*\]\]$")


def yaml_scalar(value):
    return json.dumps(value, ensure_ascii=False) if WHOLE_WIKILINK.match(value) else value


# Closed sets the guideline states in prose that its table parser cannot
# express as an enum (the parser reads `field (a/b/c)`, so a numeric set
# is invisible to it). One line per field, and the line names the rule.
# Values are compared as strings after stripping, and written bare.
CLOSED_SETS = {
    # GL-1002 / GL-002 v1.51: 1, 2 or 3; absent means not in focus. There
    # is no 0 and no "none": REMOVING the field is how a project leaves
    # focus, which is why --unset exists.
    "focus_rank": ("1", "2", "3"),
}

# Fields nothing may set from here, whatever the guideline says about
# them: they belong to a sync and a hand-written value is either lost on
# the next run or pushed to somebody else's system.
SOURCE_OWNED = {
    "external_id", "source", "source_status", "synced_at", "done_at",
    "list_id", "myicor_id", "highlight_id",
}

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

KEY = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*)\s*:(.*)$")


def load_gl_reader():
    """new-base.py's GL-1002 table parser, where it exists beside this
    script. One reader, not two: a correction to the parser lands here at
    the same moment it lands in new-base.py and check-quality.py. The
    private vault has no new-base.py; guard 2 stands down there and the
    caller is told so rather than being silently given a weaker check."""
    path = HERE / "new-base.py"
    if not path.is_file():
        return None
    try:
        spec = importlib.util.spec_from_file_location("new_base", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        for name in ("gl002_fields", "gl002_enums"):
            if not hasattr(mod, name):
                return None
        return mod
    except Exception:
        return None


def split_front(text):
    """(frontmatter, body, close_index) or (None, text, -1). Line endings
    are whatever the file had; the close fence matches either."""
    if not re.match(r"^---\r?\n", text):
        return None, text, -1
    m = noteio.FM_CLOSE.search(text, 3)
    if not m:
        return None, text, -1
    return text[text.index("\n") + 1:m.start() + 1], text[m.end():], m.start()


def read_field(front, field):
    for line in front.splitlines():
        m = KEY.match(line)
        if m and m.group(1) == field:
            return m.group(2).strip()
    return None


def unquote(v):
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        return v[1:-1]
    return v


def set_field(text, field, value, eol):
    """Rewrite exactly the one line, or append one line at the end of the
    frontmatter. Every other byte of the file is carried through."""
    front, _, close = split_front(text)
    if front is None:
        return None
    if value is not None:
        value = yaml_scalar(value)
    start = text.index("\n") + 1
    lines = front.splitlines(keepends=True)
    out, hit = [], False
    for line in lines:
        m = KEY.match(line.rstrip("\r\n"))
        if m and m.group(1) == field:
            hit = True
            if value is None:
                continue                       # --unset: drop the line
            out.append("%s: %s%s" % (field, value, eol))
        else:
            out.append(line)
    if not hit:
        if value is None:
            return text                        # --unset on an absent field
        if out and not out[-1].endswith(("\n", "\r")):
            out[-1] += eol
        out.append("%s: %s%s" % (field, value, eol))
    return text[:start] + "".join(out) + text[close + 1:]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("note")
    ap.add_argument("field", nargs="?")
    ap.add_argument("value", nargs="?")
    ap.add_argument("--unset", action="store_true")
    ap.add_argument("--show", action="store_true")
    ap.add_argument("--root", default=None)
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()

    path = Path(a.note)
    if not path.is_absolute() and a.root:
        path = Path(a.root) / a.note
    path = path.expanduser()
    if not path.is_file():
        sys.exit("FAIL no note at %s" % path)

    try:
        text, eol = noteio.read_note(path)
    except UnicodeDecodeError:
        sys.exit("FAIL %s is not UTF-8 text" % path)

    front, _, _ = split_front(text)
    if front is None:
        sys.exit("FAIL %s has no frontmatter block; this script never "
                 "creates one." % path.name)

    if a.show or not a.field:
        for line in front.splitlines():
            m = KEY.match(line)
            if m:
                print("%-20s %s" % (m.group(1), m.group(2).strip()))
        return 0

    field = a.field
    if field in SOURCE_OWNED:
        sys.exit("FAIL %r is source-owned: a sync writes it and would "
                 "overwrite anything set here." % field)

    if a.unset:
        value = None
    else:
        if a.value is None:
            sys.exit("FAIL give a value, or --unset to remove the field")
        value = a.value.strip()
        for _name, rx in SECRET_SHAPES:
            if rx.search(value):
                sys.exit("FAIL that value is secret-shaped; nothing was "
                         "written. Credentials never go in frontmatter.")
        allowed = CLOSED_SETS.get(field)
        if allowed and unquote(value) not in allowed:
            sys.exit("FAIL %s takes one of %s; got %r. (Remove the field "
                     "with --unset rather than writing a null value.)"
                     % (field, " | ".join(allowed), value))

    note_type = unquote(read_field(front, "type") or "")
    gl = load_gl_reader()
    if gl is not None and note_type:
        try:
            root = Path(a.root).resolve() if a.root else HERE.parents[3]
            declared = gl.gl002_fields(root).get(note_type)
            if declared is not None and field not in declared:
                sys.exit("FAIL %r is not declared for type %r in GL-1002. "
                         "Update the guideline first, then set the field."
                         % (field, note_type))
            enums = gl.gl002_enums(root).get(note_type, {})
            if not a.unset and field in enums and unquote(value) not in enums[field]:
                sys.exit("FAIL GL-1002 declares %s on %s as one of %s; got %r."
                         % (field, note_type, " | ".join(enums[field]), value))
        except SystemExit:
            raise
        except Exception:
            pass          # an unreadable guideline is not a reason to refuse
    elif gl is None:
        print("NOTE no new-base.py beside this script, so the GL-1002 "
              "declared-field check did not run; the closed-set check did.",
              file=sys.stderr)

    was = read_field(front, field)
    # A bare `[[X]]` left by an older version says the same thing and is still
    # broken, so it is rewritten rather than called done.
    bare = not a.unset and was == value and yaml_scalar(value) != value
    if not a.unset and was is not None and unquote(was) == unquote(value) and not bare:
        print("OK %s already %s in %s" % (field, value, path.name))
        return 0
    if a.unset and was is None:
        print("OK %s was not set in %s" % (field, path.name))
        return 0

    new = set_field(text, field, value, eol)
    if new is None:
        sys.exit("FAIL could not locate the frontmatter block in %s" % path.name)
    if a.dry:
        print("DRY %s: %s -> %s in %s"
              % (field, was, "(removed)" if a.unset else value, path.name))
        return 0
    noteio.write_note(path, new)
    print("OK %s: %s -> %s in %s"
          % (field, was, "(removed)" if a.unset else value, path.name))
    return 0


if __name__ == "__main__":
    sys.exit(main())
