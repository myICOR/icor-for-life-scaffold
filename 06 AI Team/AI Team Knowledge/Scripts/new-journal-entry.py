#!/usr/bin/env python3
"""Create a journal entry skeleton in the right place with the right name.

Usage:
  new-journal-entry.py --date 2026-08-27 --slug best-business-partner \
      --journal-type thought --original "the user's exact words"

Deterministic parts owned here: path (YYYY/MM/), filename, frontmatter
skeleton per GL-1002, the Original Text section written verbatim.
Judgement parts NOT here: choosing the journal_type (GL-1003 teaches the
four), the expansion and the connections; the model adds those to the
created file afterwards.
"""
import argparse, datetime, importlib.util, re, sys
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

DEFAULT_ROOT = Path(__file__).resolve().parents[3]
TYPES = {"interaction", "note", "thought", "milestone"}
FORMATS = {"text", "voice", "photo", "meeting-notes", "other"}

ap = argparse.ArgumentParser()
ap.add_argument("--date", required=True)
ap.add_argument("--slug", required=True)
ap.add_argument("--journal-type", required=True)
ap.add_argument("--format", help="how the entry arrived; absent = text")
ap.add_argument("--original", required=True)
ap.add_argument("--root", help="operate on another scaffold root (new-entity.py and the red tests pass it)")
ap.add_argument("--mtime-from", help="source file whose modification time this entry must carry (imports: ALWAYS pass it; recency surfaces read filesystem mtime)")
a = ap.parse_args()
ROOT = Path(a.root).resolve() if a.root else DEFAULT_ROOT

try:
    d = datetime.date.fromisoformat(a.date)
except ValueError:
    sys.exit(f"FAIL not an ISO date: {a.date}")
if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+){0,7}", a.slug):
    sys.exit(f"FAIL slug must be lowercase-hyphenated: {a.slug}")
if a.journal_type not in TYPES:
    sys.exit(f"FAIL journal-type must be one of {sorted(TYPES)}; never invent a fifth")
if a.format is not None and a.format not in FORMATS:
    sys.exit(f"FAIL format must be one of {sorted(FORMATS)}")
if not a.original.strip():
    sys.exit("FAIL empty --original; the user's words are required")

dest = ROOT / "04 Inner World/Journal" / f"{d:%Y}" / f"{d:%m}" / f"{d}_{a.slug}.md"
if dest.exists():
    sys.exit(f"FAIL entry already exists: {dest}")
dest.parent.mkdir(parents=True, exist_ok=True)
format_line = f"format: {a.format}\n" if a.format else ""
# a.original lands EXACTLY as the member said it. Until 2026-09-15 it was
# written through .strip(), which quietly ate a deliberate leading indent or
# a trailing blank line out of the one section GL-1003 calls sacred (Brian
# Carroll, T16-4). The .strip() survives only in the empty-input guard above,
# where it is asking a question rather than changing the text.
noteio.write_note(dest, f"""---
type: journal
date: {d}
journal_type: {a.journal_type}
{format_line}created: {d}
linked_people: []
linked_topics: []
linked_projects: []
---

## Original Text

{a.original}

## Expansion

""")
if a.mtime_from:
    import os, pathlib
    ref = pathlib.Path(a.mtime_from).expanduser()
    if not ref.exists():
        sys.exit(f"FAIL --mtime-from does not exist: {ref}")
    st = ref.stat()
    os.utime(dest, (st.st_atime, st.st_mtime))
print(f"OK created {dest}")
