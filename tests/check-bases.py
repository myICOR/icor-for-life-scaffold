#!/usr/bin/env python3
"""Check every .base file in the scaffold (GL-1006). Stdlib only.

Usage:
  check-bases.py [--check] [<root>]

Checks (all deterministic):
  1. Every .base parses as YAML and has the shape Obsidian expects
     (a mapping with at least one view, each view carrying a type).
  2. Every note property a base references (note.X / a bare X in a
     view order) is declared for that collection's type in GL-1002.
  3. No two .base files claim the same collection, where a collection
     is (folder, note.type) - one collection, one Base. (Found live in
     a sibling vault: a tracked People/People.base and an untracked
     People.base with different columns, each plausible, neither
     canonical.) A folder MAY carry two bases when they filter on
     different types: 04 Inner World/Notes holds Documents.base (type
     document) and Notes.base (type note) side by side. Two bases in
     one folder that do not both name a type are still one collection
     claimed twice.
Exit 0 = clean. Exit 1 = violations on stderr.
"""
import re, sys
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

# ---------------------------------------------------------------------------
# The .base reader: stdlib only, on purpose
#
# Until 2026-09-14 this file imported PyYAML, and it was the only script in
# this folder that imported anything. On a machine whose python3 has no
# PyYAML (Homebrew's, on this Mac) the import killed the script, so
# run-red-tests.py reported two check-bases gates as FAILED GUARDS when the
# guard had simply never run. A gate whose red is normal is a gate people
# learn to scroll past (tsk-2026-09-11-005), so the dependency is gone and
# the reader below is the only path, on every machine.
#
# It parses the block-YAML subset a .base file uses: comments, nested
# mappings, sequences, flow sequences and flow mappings of scalars, and the
# scalar forms Obsidian writes. It is STRICT: anything outside that subset
# raises BaseYamlError, which check-bases reports as an invalid base. Strict
# is the safe direction for a checker (it refuses more, never less), and the
# red tests below it compare every shipped .base against PyYAML whenever
# PyYAML is importable, so the reader cannot drift from real YAML unnoticed.
#
# WHAT THIS DOES NOT PROVE: that a file this reader accepts is valid YAML by
# the full spec, or that Obsidian reads it the same way. It proves the file
# is inside the subset the scaffold writes, and that its shape is the one
# GL-1006 requires.
# ---------------------------------------------------------------------------


class BaseYamlError(Exception):
    """A .base file outside the block-YAML subset this reader accepts."""


_CONSTS = {"true": True, "false": False, "yes": True, "no": False,
           "null": None, "~": None, "": None}


def _split_key(text):
    """Split `key: value` at the first colon outside quotes. Returns
    (key, found, rest); found is False when the line carries no key."""
    quote = None
    for i, ch in enumerate(text):
        if quote:
            if ch == quote:
                quote = None
            continue
        if ch in "\"'":
            quote = ch
            continue
        if ch == ":" and (i + 1 == len(text) or text[i + 1] in " \t"):
            return text[:i].strip(), True, text[i + 1:].strip()
    return text, False, ""


def _split_flow(body, lineno):
    """Split a flow body on commas that are not inside a nested flow or a
    quoted string."""
    out, depth, quote, cur = [], 0, None, ""
    for ch in body:
        if quote:
            cur += ch
            if ch == quote:
                quote = None
            continue
        if ch in "\"'":
            quote = ch
            cur += ch
            continue
        if ch in "[{":
            depth += 1
        elif ch in "]}":
            depth -= 1
            if depth < 0:
                raise BaseYamlError("line %d: unbalanced flow collection" % lineno)
        if ch == "," and depth == 0:
            out.append(cur)
            cur = ""
            continue
        cur += ch
    if quote:
        raise BaseYamlError("line %d: unterminated quoted string" % lineno)
    if depth:
        raise BaseYamlError("line %d: unbalanced flow collection" % lineno)
    if cur.strip() or out:
        out.append(cur)
    return out


def _scalar(raw, lineno):
    s = raw.strip()
    if s[:1] in ("[", "{"):
        closer = "]" if s[0] == "[" else "}"
        if not s.endswith(closer):
            raise BaseYamlError("line %d: unbalanced flow collection" % lineno)
        items = _split_flow(s[1:-1], lineno)
        if s[0] == "[":
            return [_scalar(i, lineno) for i in items]
        out = {}
        for item in items:
            k, found, v = _split_key(item.strip())
            if not found:
                raise BaseYamlError("line %d: flow mapping entry without a key" % lineno)
            out[_scalar(k, lineno)] = _scalar(v, lineno)
        return out
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "\"'":
        return s[1:-1]
    if s[:1] in ("\"", "'"):
        raise BaseYamlError("line %d: unterminated quoted string" % lineno)
    low = s.lower()
    if low in _CONSTS:
        return _CONSTS[low]
    try:
        return int(s)
    except ValueError:
        pass
    try:
        return float(s)
    except ValueError:
        pass
    return s


def _tokens(text):
    out = []
    for n, raw in enumerate(text.splitlines(), 1):
        body = raw.strip()
        if not body or body.startswith("#"):
            continue
        lead = raw[: len(raw) - len(raw.lstrip())]
        if "\t" in lead:
            raise BaseYamlError("line %d: tab in indentation" % n)
        out.append([n, len(lead), body])
    return out


def _is_item(text):
    return text == "-" or text.startswith("- ")


def _block(toks, i):
    return _seq(toks, i) if _is_item(toks[i][2]) else _map(toks, i)


def _guard_tail(toks, i, indent):
    if i < len(toks) and toks[i][1] > indent:
        raise BaseYamlError("line %d: unexpected indentation" % toks[i][0])


def _seq(toks, i):
    indent = toks[i][1]
    items = []
    while i < len(toks) and toks[i][1] == indent and _is_item(toks[i][2]):
        n, _, text = toks[i]
        body = text[1:].strip()
        if not body:
            i += 1
            if i < len(toks) and toks[i][1] > indent:
                v, i = _block(toks, i)
            else:
                v = None
            items.append(v)
            continue
        inner = indent + (len(text) - len(text[1:].lstrip()))
        _, found, _ = _split_key(body)
        if found and body[:1] not in ("[", "{", "\"", "'"):
            toks[i] = [n, inner, body]
            v, i = _map(toks, i)
            items.append(v)
        else:
            items.append(_scalar(body, n))
            i += 1
    _guard_tail(toks, i, indent)
    return items, i


def _map(toks, i):
    indent = toks[i][1]
    out = {}
    while i < len(toks) and toks[i][1] == indent:
        n, _, text = toks[i]
        if _is_item(text):
            raise BaseYamlError("line %d: list item where a mapping key was expected" % n)
        key, found, rest = _split_key(text)
        if not found:
            raise BaseYamlError("line %d: not a mapping key (%r)" % (n, text))
        i += 1
        if rest:
            out[key] = _scalar(rest, n)
            continue
        if i < len(toks) and toks[i][1] > indent:
            out[key], i = _block(toks, i)
        else:
            out[key] = None
    _guard_tail(toks, i, indent)
    return out, i


def load_base(text):
    """Parse a .base file. Raises BaseYamlError on anything outside the subset."""
    toks = _tokens(text)
    if not toks:
        return None
    if toks[0][1] != 0:
        raise BaseYamlError("line %d: the file starts indented" % toks[0][0])
    doc, i = _block(toks, 0)
    if i != len(toks):
        raise BaseYamlError("line %d: trailing content the reader cannot place" % toks[i][0])
    return doc


def blob(node, out=None):
    """Every key and every scalar in the document, one per line. The
    expressions check-bases greps for (file.inFolder(...), note.type == ...,
    note.<field>) all land here, and comments do not, which a raw read of the
    file text could not promise."""
    if out is None:
        out = []
    if isinstance(node, dict):
        for k, v in node.items():
            out.append(str(k))
            blob(v, out)
    elif isinstance(node, list):
        for v in node:
            blob(v, out)
    elif node is not None:
        out.append(str(node))
    return "\n".join(out)


HERE = Path(__file__).resolve().parent
# NO sys.path.insert HERE. new-base.py is loaded BY PATH on the next four
# lines, so nothing about this import needs Scripts/ on sys.path; the insert
# was dead code that put Scripts/ at the FRONT of it, which is exactly the F1
# hole every guard in this folder now closes on its first statement. A planted
# `Scripts/json.py` would have won over the standard library from here on
# (Vex F-F, 2026-09-16).
import importlib.util
_spec = importlib.util.spec_from_file_location("new_base", HERE / "new-base.py")
new_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(new_base)

argv = [a for a in sys.argv[1:] if a != "--check"]
ROOT = Path(argv[0]).resolve() if argv else HERE.parents[2]
fails = []

# GL-1002 declares fields per type; a base's columns must live there.
try:
    DECLARED = new_base.gl002_fields(ROOT)
except OSError as exc:
    sys.exit("FAIL cannot read GL-1002: %s" % exc)

# (folder as filtered, note.type as filtered or None) -> the base that claims it
claimed = {}
# containing directory -> bases sitting in it
per_dir = {}
# base -> the type it filters on (None when it names none)
base_type = {}

bases = sorted(p for p in ROOT.rglob("*.base") if ".obsidian" not in p.parts)
for b in bases:
    rel = b.relative_to(ROOT)
    per_dir.setdefault(b.parent, []).append(rel)
    try:
        doc = load_base(b.read_text(encoding="utf-8"))
    except BaseYamlError as exc:
        fails.append("%s: not valid YAML (%s)" % (rel, str(exc).splitlines()[0]))
        continue
    if not isinstance(doc, dict):
        fails.append("%s: base must be a YAML mapping" % rel)
        continue
    views = doc.get("views")
    if not isinstance(views, list) or not views:
        fails.append("%s: base has no views" % rel)
        continue
    for v in views:
        if not isinstance(v, dict) or not v.get("type"):
            fails.append("%s: a view is missing its type" % rel)

    # which folder does this base claim, and which entity type
    text = blob(doc)
    folders = re.findall(r'file\.inFolder\("([^"]+)"\)', text)
    types = re.findall(r'note\.type\s*==\s*"([^"]+)"', text)
    base_type[rel] = types[0] if types else None
    for f in folders:
        key = (f, base_type[rel])
        if key in claimed and claimed[key] != rel:
            fails.append("two bases claim the same collection %r (type %s): %s and %s "
                         "(GL-1006: one collection, one Base)"
                         % (f, base_type[rel] or "any", claimed[key], rel))
        else:
            claimed[key] = rel

    # every referenced note property must be GL-1002-declared
    if types:
        declared = DECLARED.get(types[0])
        if declared is None:
            fails.append("%s: filters on note.type %r, which GL-1002 does "
                         "not declare" % (rel, types[0]))
        else:
            props = set(re.findall(r"note\.([a-z][a-z0-9_]*)", text))
            props |= {k for k in (doc.get("properties") or {})
                      if isinstance(k, str) and not k.startswith("file.")
                      and not k.startswith("note.")}
            for p in sorted(props - {"type"}):
                if p not in declared:
                    fails.append("%s: column note.%s is not a GL-1002 field "
                                 "for type %r (update the guideline first)"
                                 % (rel, p, types[0]))

for d, blist in per_dir.items():
    if len(blist) > 1:
        # Two bases in one folder are two collections only when every one
        # of them names a distinct note.type; a base with no type filter
        # claims the whole folder.
        seen = [base_type.get(b) for b in blist]
        if None in seen or len(set(seen)) != len(seen):
            fails.append("folder %s carries %d base files (%s) that do not "
                         "split by note.type; GL-1006 allows one Base per collection"
                         % (d.relative_to(ROOT), len(blist),
                            ", ".join(b.name for b in blist)))

if fails:
    for m in fails:
        print("FAIL %s" % m, file=sys.stderr)
    sys.exit(1)
print("OK %d base file(s) valid, one per collection" % len(bases))
