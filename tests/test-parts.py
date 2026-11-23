#!/usr/bin/env python3
"""test-parts.py: what is core and what is optional (Tom, 2026-11-23), kept in step, and the optional pieces really
optional. _System/parts.json, README.md and AGENTS.md name the same pieces; every bundled plugin is one or the other;
the two databases are exactly their schemas and hold no data; nothing core refers to an optional piece; and the folder
still checks out with every optional piece removed. Exit 0 when every case holds."""
import json, re, shutil, sqlite3, subprocess, sys, tempfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent.parent
fails, checks = [], 0


def check(name, ok, detail=""):
    global checks
    checks += 1
    print(("  ok   " if ok else "  FAIL ") + name + ("" if ok else f": {detail}"))
    if not ok:
        fails.append(name)


parts = json.loads((ROOT / "_System/parts.json").read_text())
lock = json.loads((ROOT / "release/plugins.lock.json").read_text())
enabled = json.loads((ROOT / ".obsidian/community-plugins.json").read_text())
core_ids = {p["id"] for p in parts["core"] if p.get("id")}
opt_ids = {p["id"] for p in parts["optional"] if p.get("id")}
lock_ids = {p["id"] for p in lock["plugins"]}

print("one list")
check("every bundled plugin is core or optional, once", lock_ids == core_ids | opt_ids and not core_ids & opt_ids,
      sorted(lock_ids ^ (core_ids | opt_ids)))
check("everything bundled is turned on, out of the box", set(enabled) == lock_ids, sorted(set(enabled) ^ lock_ids))
check("SQLite Viewer ships and is optional", "icor-for-life-sqlite-viewer" in opt_ids and "icor-for-life-sqlite-viewer" in lock_ids)
for p in parts["optional"]:
    check(f"{p['name']}: how to remove it and what stops working", bool(p.get("remove")) and bool(p.get("stops")), p)

print("said the same in README and AGENTS")
readme, agents = (ROOT / "README.md").read_text(), (ROOT / "AGENTS.md").read_text()
for p in parts["core"] + parts["optional"]:
    if p["kind"] in ("plugin", "database", "theme"):
        name = p.get("path") or p["name"].replace(" (theme)", "")
        for doc, text in (("README.md", readme), ("AGENTS.md", agents)):
            check(f"{doc} names {name}", name in text)
check("AGENTS.md keeps health and money in their databases", "never copy rows into a note" in agents.lower() and "through SQL" in agents)

print("the databases")
dbreadme = (ROOT / "05 Databases/README.md").read_text()
for kind, file in (("health", "Health.sqlite"), ("finance", "Finance.sqlite")):
    sql = (ROOT / f"_System/Databases/{kind}.sql").read_text()
    fresh = sqlite3.connect(":memory:"); fresh.executescript(sql)
    shipped = sqlite3.connect(f"file:{ROOT / '05 Databases' / file}?mode=ro", uri=True)
    shape = lambda c: sorted(c.execute("SELECT type, name, sql FROM sqlite_master WHERE name NOT LIKE 'sqlite_%'").fetchall())
    check(f"{file} is exactly {kind}.sql", shape(fresh) == shape(shipped))
    tables = [n for (n,) in shipped.execute("SELECT name FROM sqlite_master WHERE type IN ('table','view') AND name NOT LIKE 'sqlite_%'")]
    full = [n for n in tables if n not in ("about", "categories")
            and shipped.execute("SELECT type FROM sqlite_master WHERE name = ?", (n,)).fetchone()[0] == "table"
            and shipped.execute(f'SELECT COUNT(*) FROM "{n}"').fetchone()[0]]
    check(f"{file} holds no data (only about and the starter categories)", not full, full)
    check(f"05 Databases/README.md describes every table of {file}", all(f"`{n}`" in dbreadme for n in tables),
          [n for n in tables if f"`{n}`" not in dbreadme])

print("nothing core depends on an optional piece")
ALLOWED = {"README.md", "AGENTS.md", "05 Databases/README.md", "_System/parts.json", "_System/Tools/new-database.py",
           "_System/Tools/README.md", ".obsidian/community-plugins.json", "release/plugins.lock.json", ".icor-for-life/CHANGELOG.md",
           "SECURITY.md", ".icor-for-life/THIRD-PARTY-NOTICES.md"}
OPTIONAL_WORDS = re.compile(r"Health\.sqlite|Finance\.sqlite|sqlite-viewer|SQLite Viewer")
tracked = subprocess.check_output(["git", "-C", str(ROOT), "ls-files"], text=True).splitlines()
leaks = []
for f in tracked:
    p = ROOT / f
    if f in ALLOWED or f.startswith(("tests/", "_System/Databases/")) or not p.is_file() or p.suffix in (".sqlite", ".png", ".jpg"):
        continue
    try:
        if OPTIONAL_WORDS.search(p.read_text(encoding="utf-8")):
            leaks.append(f)
    except UnicodeDecodeError:
        pass
check("only the documentation names the optional databases and SQLite Viewer", not leaks, leaks)

print("the folder without the optional pieces")
with tempfile.TemporaryDirectory(prefix="test-parts.") as tmp:
    full = Path(tmp) / "full"
    slim = Path(tmp) / "slim"
    ignore = shutil.ignore_patterns(".git", "release", "tests", "__pycache__")
    shutil.copytree(ROOT, full, ignore=ignore)
    shutil.copytree(ROOT, slim, ignore=ignore)
    for p in parts["optional"]:
        if p["kind"] == "database":
            (slim / p["path"]).unlink()
    (slim / ".obsidian/community-plugins.json").write_text(json.dumps(sorted(set(enabled) - opt_ids), indent=2))
    run = lambda v, *a: subprocess.run([sys.executable, str(v / "_System/Tools" / a[0]), *a[1:]], capture_output=True, text=True, cwd=v)
    a, b = run(full, "check-quality.py", str(full), "--json"), run(slim, "check-quality.py", str(slim), "--json")
    fa, fb = json.loads(a.stdout or "{}"), json.loads(b.stdout or "{}")
    strip = lambda r: sorted((x.get("metric"), x.get("path")) for x in r.get("findings", []))
    check("check-quality reads the folder the same with and without them", a.returncode == b.returncode and strip(fa) == strip(fb),
          (a.returncode, b.returncode, a.stderr[-300:], b.stderr[-300:]))
    check("the core plugins stay turned on", core_ids <= set(json.loads((slim / ".obsidian/community-plugins.json").read_text())))
    r = run(slim, "new-database.py", "health")
    check("a deleted database can be made again, empty", r.returncode == 0 and (slim / "05 Databases/Health.sqlite").is_file(), r.stdout + r.stderr)
    r = run(slim, "new-database.py", "health")
    check("and is never made over one that exists", r.returncode != 0 and "left as it is" in (r.stdout + r.stderr), r.stdout + r.stderr)

if fails:
    print("FAIL %d of %d cases" % (len(fails), checks))
    sys.exit(1)
print("OK %d cases held" % checks)
