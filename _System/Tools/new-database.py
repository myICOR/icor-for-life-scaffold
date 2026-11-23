#!/usr/bin/env python3
"""new-database.py: make one of the optional databases in 05 Databases, empty, from its schema in _System/Databases.

    python3 _System/Tools/new-database.py health      05 Databases/Health.sqlite
    python3 _System/Tools/new-database.py finance     05 Databases/Finance.sqlite
    python3 _System/Tools/new-database.py --list      what can be made, and what is there

A database that exists is never touched: delete it yourself first if you want it new and empty. Health and finance
data stays in these files on this computer: no note copies it and nothing sends it anywhere. Both are optional; see
"What's core, what's optional" in README.md.
"""
import sqlite3, sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
VAULT = HERE.parents[1]
SCHEMAS = HERE.parent / "Databases"
FOLDER = "05 Databases"
NAMES = {"health": "Health.sqlite", "finance": "Finance.sqlite"}


def make(kind: str, vault: Path = VAULT) -> Path:
    if kind not in NAMES:
        raise SystemExit(f"FAIL no database called {kind}: {', '.join(NAMES)}")
    sql = (SCHEMAS / f"{kind}.sql").read_text(encoding="utf-8")
    folder = vault / FOLDER
    if not folder.is_dir():
        raise SystemExit(f"FAIL {FOLDER}/ is not in {vault}")
    target = folder / NAMES[kind]
    if target.exists():
        raise SystemExit(f"FAIL {FOLDER}/{NAMES[kind]} exists already and is left as it is; delete it first for a new one")
    tmp = target.with_name(f".{target.name}.new")
    tmp.unlink(missing_ok=True)
    con = sqlite3.connect(tmp)
    try:
        con.executescript(sql)
        con.commit()
    finally:
        con.close()
    tmp.replace(target)
    return target


def main():
    args = sys.argv[1:]
    if args == ["--list"]:
        for kind, name in NAMES.items():
            have = (VAULT / FOLDER / name).exists()
            print(f"  {kind:8} {FOLDER}/{name}  {'there' if have else 'not made'}")
        return
    if len(args) != 1:
        raise SystemExit(__doc__)
    t = make(args[0])
    print(f"OK {t.relative_to(VAULT)} made, empty, from _System/Databases/{args[0]}.sql")


if __name__ == "__main__":
    main()
