#!/usr/bin/env python3
"""Find the entity note a name or an alias belongs to. JSON out.

Usage:
  find-entity.py "<name or alias>" [--type person|company|...]...
  find-entity.py "<name>" --root <vault-root>

The duplicate check before creating anything (SOP-1004 step 1, SOP-1005
step 1): one thing, one note, forever. Run this before new-entity.py, and
before the member is asked to type a name twice.

What counts as a match, in the order a person would try them:
  1. the filename (`Alex Rivera.md`), the way Obsidian resolves `[[Alex Rivera]]`
  2. frontmatter `name` (person, company, habit) or `title`
  3. any entry in frontmatter `aliases`

Matching is exact after normalising: case folded, surrounding whitespace
dropped, inner runs of whitespace collapsed to one space. It is NOT fuzzy
on purpose: a near miss reported as a hit is how two notes for one person
get merged into the wrong one. Near misses are the duplicate_entities
metric in check-quality.py, which is a question for the member, not an
answer from a script.

Exit 0 = at least one hit. Exit 2 = none (a clean "create it"). Exit 1 =
refused: no name, an unknown --type, a root that is not a scaffold.
"""
import argparse, json, re, sys
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

# Where entities live, by type. Same rooms new-entity.py files into; read
# from there so the two cannot drift.
import importlib.util
_spec = importlib.util.spec_from_file_location("new_entity", HERE / "new-entity.py")
new_entity = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(new_entity)
ROOMS = {t: f for t, f in new_entity.ROOMS.items() if t != "journal"}


def norm(s):
    return re.sub(r"\s+", " ", (s or "").strip()).casefold()


def unquote(v):
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        v = v[1:-1]
    return v.strip()


def alias_values(raw):
    """The entries of an inline `aliases: [a, b]` value."""
    raw = raw.strip()
    if raw.startswith("[") and raw.endswith("]"):
        return [unquote(v) for v in raw[1:-1].split(",") if v.strip()]
    return [unquote(raw)] if raw else []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("name", nargs="?")
    ap.add_argument("--type", action="append", default=[],
                    help="limit to a type; repeatable")
    ap.add_argument("--root", default=None)
    a = ap.parse_args()

    if not a.name or not a.name.strip():
        sys.exit("FAIL give a name or an alias to look for")
    root = Path(a.root).resolve() if a.root else DEFAULT_ROOT
    if not (root / "02 Inner World").is_dir():
        sys.exit("FAIL %s is not a scaffold root (no '02 Inner World')" % root)
    for t in a.type:
        if t not in ROOMS:
            sys.exit("FAIL unknown --type %r; known: %s"
                     % (t, ", ".join(sorted(ROOMS))))

    wanted = a.type or sorted(ROOMS)
    key = norm(a.name)
    hits = []
    seen = set()
    for t in wanted:
        folder = root / ROOMS[t]
        if not folder.is_dir():
            continue
        for f in sorted(folder.rglob("*.md")):
            if f.name == "README.md" or f in seen:
                continue
            text = f.read_text(encoding="utf-8", errors="ignore")
            fm = new_entity.read_frontmatter(text)
            ftype = unquote(fm.get("type", ""))
            if a.type and ftype and ftype != t:
                continue          # two types share the Notes folder
            names = {"filename": f.stem}
            for field in ("name", "title"):
                if fm.get(field):
                    names[field] = unquote(fm[field])
            aliases = alias_values(fm.get("aliases", ""))
            matched = [w for w, v in names.items() if norm(v) == key]
            matched += ["alias:%s" % v for v in aliases if norm(v) == key]
            if matched:
                seen.add(f)
                hits.append({
                    "path": f.relative_to(root).as_posix(),
                    "name": names.get("name") or names.get("title") or f.stem,
                    "type": ftype or t,
                    "aliases": aliases,
                    "matched_on": matched,
                })
    print(json.dumps({"query": a.name, "root": str(root),
                      "count": len(hits), "hits": hits}, indent=2))
    return 0 if hits else 2


if __name__ == "__main__":
    sys.exit(main())
