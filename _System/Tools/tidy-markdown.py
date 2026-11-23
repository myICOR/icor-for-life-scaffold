#!/usr/bin/env python3
"""tidy-markdown.py: two tidy-ups Obsidian needs, and the check that keeps them tidy.

    python3 _System/Tools/tidy-markdown.py tops [folder]             what would change at the top of each note
    python3 _System/Tools/tidy-markdown.py tops [folder] --live      change it; every changed note is backed up first
    python3 _System/Tools/tidy-markdown.py unwrap <file>... [--live] one line per paragraph and per list item
    python3 _System/Tools/tidy-markdown.py check <file or folder>... exit 1 when a paragraph is hard-wrapped
    python3 _System/Tools/tidy-markdown.py restore <backup folder>   put a backup back

tops: Obsidian shows the file name as the note's title, so a note needs no `# Title` of its own, and a blank line right
after the properties shows as an empty first line. It removes the blank lines right after the properties, and a first
`# Heading` only when it is the file name (ignoring case, spaces, hyphens and punctuation) or `{{title}}` in a
template, with the blank lines under it. Nothing else in a note is touched. Without --live it changes nothing and lists
what it would do. With --live each note it changes is copied first to .icor-for-life/backups/tidy-markdown-<time>/.

unwrap and check: Obsidian shows every newline as a line break (strictLineBreaks is off), so Markdown written for a
narrow editor, wrapped at 80 or 120 characters, shows broken lines. unwrap joins a paragraph's lines into one, and a
list item's indented lines into the item. Front matter, code blocks, tables, headings, quotes and callouts, embeds,
HTML and a line ending in a deliberate break (two spaces or a backslash) are left as they are.
"""
import re, shutil, sys, time
from pathlib import Path

sys.dont_write_bytecode = True
SKIP_DIRS = {".obsidian", ".git", ".trash", ".icor-for-life", "node_modules", ".mypka", "06 AI Team", ".agents", ".claude"}
FENCE = re.compile(r"^\s*(```|~~~)")
BLOCK = re.compile(r"^\s*(#{1,6}\s|[-*+]\s|\d+[.)]\s|\||>|<|!\[\[|\[\^|\$\$|([-*_])(\s*\2){2,}\s*$)")
LIST = re.compile(r"^(\s*)([-*+]|\d+[.)])\s")


def split_front(text):
    """(front matter including its fences, body). No front matter: ('', text)."""
    if text.startswith("---\n"):
        end = text.find("\n---\n", 3)
        if end >= 0:
            return text[: end + 5], text[end + 5:]
        if text.endswith("\n---"):
            return text + "\n", ""
    return "", text


def norm(s):
    return re.sub(r"[\W_]+", "", s.lower())


def tidy_top(text, stem):
    """The note with a tidy top, and what changed (a list of short words)."""
    front, body = split_front(text)
    changed = []
    if front:
        stripped = body.lstrip("\n")
        if stripped != body:
            changed.append("blank line")
            body = stripped
    m = re.match(r"# (.+?)\s*\n", body + ("\n" if not body.endswith("\n") else ""))
    if m and (norm(m.group(1)) == norm(stem) or m.group(1).strip() == "{{title}}"):
        rest = body[m.end():] if m.end() <= len(body) else ""
        body = rest.lstrip("\n")
        changed.append("title heading")
    return front + body, changed


def unwrap(text):
    """(the text with one line per paragraph and per list item, the number of lines joined)."""
    front, body = split_front(text)
    out, joined, fenced = [], 0, False
    for line in body.split("\n"):
        if FENCE.match(line):
            fenced = not fenced
            out.append(line)
            continue
        prev = out[-1] if out else ""
        can_join = (not fenced and line.strip() and not BLOCK.match(line) and prev.strip() and not FENCE.match(prev)
                    and not re.match(r"^\s*(#{1,6}\s|\||>|<|!\[\[|\$\$)", prev) and not prev.endswith(("  ", "\\")))
        if can_join and not LIST.match(prev) and line[:1].isspace() and not out_in_list(out):
            can_join = False          # indented text after a paragraph is a code block or a continuation we leave
        if can_join:
            out[-1] = prev.rstrip() + " " + line.strip()
            joined += 1
        else:
            out.append(line)
    return front + "\n".join(out), joined


def out_in_list(out):
    """True when the last block is a list item (its continuation lines are indented)."""
    for line in reversed(out):
        if not line.strip():
            return False
        if LIST.match(line):
            return True
    return False


def md_files(paths):
    for p in map(Path, paths):
        if p.is_file() and p.suffix == ".md":
            yield p
        elif p.is_dir():
            for f in sorted(p.rglob("*.md")):
                if not SKIP_DIRS & set(f.relative_to(p).parts):
                    yield f


def write(p: Path, text: str):
    tmp = p.with_name(f".{p.name}.tidy")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(p)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    live = "--live" in sys.argv
    if not args or args[0] not in ("tops", "unwrap", "check", "restore"):
        sys.exit(__doc__)
    cmd, rest = args[0], args[1:]

    if cmd == "restore":
        if len(rest) != 1 or not (Path(rest[0]) / "PATHS").is_file():
            sys.exit("FAIL give the backup folder tidy-markdown made (it holds a PATHS file)")
        b = Path(rest[0])
        root = Path((b / "PATHS").read_text(encoding="utf-8").splitlines()[0])
        n = 0
        for f in sorted(x for x in b.rglob("*.md")):
            write(root / f.relative_to(b), f.read_text(encoding="utf-8"))
            n += 1
        print(f"OK {n} notes put back as they were")
        return

    if cmd == "tops":
        root = Path(rest[0] if rest else ".").resolve()
        backup = root / ".icor-for-life/backups" / time.strftime("tidy-markdown-%Y%m%d-%H%M%S")
        counts, examples = {"blank line": 0, "title heading": 0}, []
        notes = 0
        for f in md_files([root]):
            try:
                text = f.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            new, changed = tidy_top(text, f.stem)
            if not changed:
                continue
            notes += 1
            for c in changed:
                counts[c] += 1
            if len(examples) < 8:
                examples.append(f"{f.relative_to(root)}: {' and '.join(changed)}")
            if live:
                keep = backup / f.relative_to(root)
                keep.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, keep)
                write(f, new)
        if live and notes:
            (backup / "PATHS").write_text(str(root) + "\n", encoding="utf-8")
        print(f"{'Changed' if live else 'Would change'} {notes} notes: {counts['blank line']} blank lines after the properties, "
              f"{counts['title heading']} title headings")
        for e in examples:
            print(f"  {e}")
        if live and notes:
            print(f"OK the originals are in {backup.relative_to(root)}; to undo: tidy-markdown.py restore \"{backup}\"")
        elif not live:
            print("OK nothing changed. Run again with --live to do it.")
        return

    total, files = 0, []
    for f in md_files(rest):
        text = f.read_text(encoding="utf-8")
        new, n = unwrap(text)
        if n:
            total += n
            files.append((f, n))
            if cmd == "unwrap" and live:
                write(f, new)
    for f, n in files:
        print(f"  {f}: {n} line{'s' if n != 1 else ''} {'joined' if cmd == 'unwrap' and live else 'run on into the next'}")
    if cmd == "check":
        if files:
            print(f"FAIL {total} hard-wrapped line(s) in {len(files)} file(s): one paragraph per line (tidy-markdown.py unwrap)")
            sys.exit(1)
        print("OK no hard-wrapped Markdown")
    else:
        print(f"{'Joined' if live else 'Would join'} {total} line(s) in {len(files)} file(s)" + ("" if live else ". Run again with --live to do it."))


if __name__ == "__main__":
    main()
