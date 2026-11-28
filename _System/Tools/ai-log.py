#!/usr/bin/env python3
"""ai-log.py: adds one entry to today's AI log, 09 AI/Log/YYYY/MM/YYYY-MM-DD.md.

    python3 _System/Tools/ai-log.py --who Claude --where "08 Workbench/2026-11-28 Webinar outline" \
        "Drafted outline.md from the brief" "Changed nothing outside the Workbench"

Every AI that changes something in this folder logs it here: when, who, where, and one line per change. The file is
made on the first entry of the day; later entries are appended under their own heading. Earlier entries are never
touched. Prints OK <path> or FAIL <why>.
"""
import argparse, datetime, sys
from pathlib import Path

sys.dont_write_bytecode = True
DEFAULT_ROOT = Path(__file__).resolve().parents[2]
LOG = "09 AI/Log"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("lines", nargs="+", help="what changed, one line each")
    ap.add_argument("--who", required=True, help="which AI: Claude, ChatGPT, Codex…")
    ap.add_argument("--where", default="", help="the folder or note the work was in")
    ap.add_argument("--at", help="the moment, YYYY-MM-DDTHH:MM (default: now, this computer's time)")
    ap.add_argument("--root", help="another ICOR for Life folder (the tests pass it)")
    a = ap.parse_args()
    root = Path(a.root).resolve() if a.root else DEFAULT_ROOT
    if not (root / "_System/schema.json").is_file():
        sys.exit(f"FAIL {root} is not an ICOR for Life folder (no _System/schema.json)")
    try:
        at = datetime.datetime.fromisoformat(a.at) if a.at else datetime.datetime.now()
    except ValueError:
        sys.exit(f"FAIL --at {a.at!r} is not YYYY-MM-DDTHH:MM")
    lines = [" ".join(l.split()) for l in a.lines if l.strip()]
    if not lines:
        sys.exit("FAIL nothing to log: give at least one line")
    who = " ".join(a.who.split())
    if not who:
        sys.exit("FAIL --who is empty")
    day = at.date().isoformat()
    path = root / LOG / f"{at:%Y}" / f"{at:%m}" / f"{day}.md"
    head = f"## {at:%H:%M} · {who}" + (f" · {' '.join(a.where.split())}" if a.where.strip() else "")
    entry = head + "\n" + "".join(f"- {l}\n" for l in lines)
    if path.exists():
        text = path.read_text(encoding="utf-8")
        sep = "" if text.endswith("\n\n") else ("\n" if text.endswith("\n") else "\n\n")
        with path.open("a", encoding="utf-8") as f:
            f.write(sep + entry)
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"---\ntype: log\ndate: {day}\ncreated: {day}\n---\n{entry}", encoding="utf-8")
    print(f"OK {path.relative_to(root)}")


if __name__ == "__main__":
    main()
