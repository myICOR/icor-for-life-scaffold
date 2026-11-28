#!/usr/bin/env python3
"""guard-paths.py: Claude Code's PreToolUse hook for Write, Edit and MultiEdit in an ICOR for Life folder.

It refuses, with the reason and where the file belongs:
  - a file in the folder's top level, except its own pages (README.md, AGENTS.md, AboutMe.md, CLAUDE.md, LICENSE.md, SECURITY.md)
    and dot files;
  - a file inside the folder but outside its folders (the numbered folders in _System/schema.json, _System, and dot
    folders such as .claude, .agents, .obsidian, .icor-for-life).
Paths outside the folder are not this hook's business. Wired in .claude/settings.json; reads the hook's JSON on stdin.
Exit 0 lets the write through; exit 2 refuses it and Claude reads the message.

    python3 _System/Tools/guard-paths.py --check "<path>"     the same verdict for one path, for people and tests
"""
import json, os, sys
from pathlib import Path

sys.dont_write_bytecode = True
KEEP = {"readme.md", "agents.md", "aboutme.md", "claude.md", "license.md", "security.md"}
LEGACY = {"06 AI Team"}       # a 2.x room a migrated folder may still hold (a myPKA team lives there); 03 WiP is gone in 3.0
IMAGE = {"png", "jpg", "jpeg", "gif", "webp", "heic", "heif", "avif", "svg", "bmp", "tif", "tiff", "mp4", "mov", "m4v", "webm"}
AUDIO = {"mp3", "m4a", "wav", "aac", "flac", "ogg", "opus", "aif", "aiff", "caf"}
DOCUMENT = {"pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx", "odt", "ods", "odp", "rtf", "pages", "numbers", "key", "epub", "txt", "csv"}


def vault_of(start: Path):
    """The ICOR for Life folder a path is in: the nearest folder above it with _System/schema.json."""
    for d in [start, *start.parents]:
        if (d / "_System/schema.json").is_file():
            return d
    return None


def rooms_of(vault: Path):
    try:
        s = json.loads((vault / "_System/schema.json").read_text(encoding="utf-8"))
        return list(s.get("folders") or s.get("rooms") or {})      # `rooms` in a schema from before the ICOR stages
    except (OSError, ValueError):
        return []


def home_for(name: str, rooms):
    """Where a file of this kind belongs (the same rule as the Objects plugin's top-folder guard)."""
    inbox = next((r for r in rooms if "inbox" in r.lower()), "01 Inbox")
    assets = next((r for r in rooms if r.lower().endswith((" files", " assets"))), "10 Files")
    ext = name.rsplit(".", 1)[-1].lower() if "." in name else ""
    if ext in IMAGE: return f"{assets}/Images/"
    if ext in AUDIO: return f"{assets}/Audio/"
    if ext in DOCUMENT: return f"{assets}/Documents/"
    if ext == "md": return f"the folder the note belongs in (a typed note: its type's folder in _System/schema.json; unsorted: {inbox}/)"
    return f"{inbox}/"


def verdict(path_text: str, cwd: str):
    """None when the write may go ahead, else the message that refuses it."""
    p = Path(path_text)
    if not p.is_absolute():
        p = Path(cwd) / p
    p = Path(os.path.normpath(str(p)))
    vault = vault_of(p.parent if p.parent.exists() else next((a for a in p.parents if a.exists()), p.parent))
    if not vault:
        return None
    rel = p.relative_to(vault)
    parts = rel.parts
    if not parts:
        return None
    rooms = rooms_of(vault)
    if len(parts) == 1:
        name = parts[0]
        if name.startswith(".") or name.lower() in KEEP:
            return None
        return (f"Refused: {name} would land in the top folder of this ICOR for Life folder, which holds only README.md, "
                f"AGENTS.md and the numbered folders. Put it in {home_for(name, rooms)} instead. AGENTS.md (\"Where files go\") has the rule.")
    top = parts[0]
    if top.startswith(".") or top == "_System" or top in rooms or top in LEGACY:
        return None
    return (f"Refused: {top}/ is not one of this vault's folders ({', '.join(rooms)}). Put {parts[-1]} in "
            f"{home_for(parts[-1], rooms)} instead. AGENTS.md (\"Where files go\") has the rule.")


def main():
    if len(sys.argv) == 3 and sys.argv[1] == "--check":
        v = verdict(sys.argv[2], os.getcwd())
        print(v or "OK it may be written there")
        sys.exit(2 if v else 0)
    try:
        event = json.load(sys.stdin)
    except ValueError:
        sys.exit(0)                       # nothing readable: not ours to stop
    tool_input = event.get("tool_input") or {}
    path = tool_input.get("file_path") or tool_input.get("notebook_path")
    if not path:
        sys.exit(0)
    v = verdict(path, event.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
    if v:
        print(v, file=sys.stderr)
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
