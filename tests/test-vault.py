#!/usr/bin/env python3
"""test-vault.py: the structure of the ICOR for Life 3.0 folder, checked from the repository.

The schema, the folders, the templates, the skills, AGENTS.md and the Obsidian settings must agree with each other:
each one is read by something else (the scripts, the Objects plugin, the AI tools), and a disagreement fails quietly
in front of a member. Exit 0 when every case holds."""
import json, re, subprocess, sys
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


schema = json.loads((ROOT / "_System/schema.json").read_text(encoding="utf-8"))
types = schema["types"]

# --- the schema holds together -------------------------------------------------------------------------------------
for t, v in types.items():
    for field, link in v["links"].items():
        check(f"schema: {t}.{field} points to a type that exists", link["to"] in types, link["to"])
    for field, vals in v["values"].items():
        check(f"schema: {t}.{field} has a closed set of two or more", isinstance(vals, list) and len(vals) > 1, vals)
    check(f"schema: {t}'s required fields are among its fields", set(v["required"]) <= set(v["fields"]) | {"type"},
          sorted(set(v["required"]) - set(v["fields"])))

# --- every type a person makes has its folder and its template -----------------------------------------------------
for t, v in types.items():
    if v["owner"] != "you" or not v["folder"] or t in ("capture",):
        continue
    check(f"folder for {t}: {v['folder']}", (ROOT / v["folder"]).is_dir())
    if v["template"]:
        tp = ROOT / "_System/Templates" / v["template"]
        check(f"template for {t}: {v['template']}", tp.is_file())
        if tp.is_file():
            m = re.search(r"^type:\s*(\S+)", tp.read_text(encoding="utf-8"), re.M)
            check(f"template {v['template']} says type: {t}", bool(m) and m.group(1) == t, m.group(1) if m else None)
for room in schema["rooms"]:
    check(f"room exists: {room}", (ROOT / room).is_dir())

# --- the skills ------------------------------------------------------------------------------------------------------
skills = sorted(p for p in (ROOT / "_System/Skills").iterdir() if p.is_dir())
check("nine skills", len(skills) == 9, [p.name for p in skills])
agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
for sk in skills:
    md = (sk / "SKILL.md").read_text(encoding="utf-8")
    m = re.match(r"---\nname: (.+)\ndescription: (.+)\n---\n", md)
    check(f"skill {sk.name}: frontmatter with name and description", bool(m))
    check(f"skill {sk.name}: its name is its folder", bool(m) and m.group(1).strip() == sk.name)
    check(f"skill {sk.name}: AGENTS.md lists it", f"`{sk.name}`" in agents)
    for tool in set(re.findall(r"_System/Tools/([a-z-]+\.py)", md)):
        check(f"skill {sk.name}: the tool {tool} exists", (ROOT / "_System/Tools" / tool).is_file())
    for other in set(re.findall(r"skill \*\*([a-z-]+)\*\*", md)):
        check(f"skill {sk.name}: the skill it names, {other}, exists", (ROOT / "_System/Skills" / other).is_dir())

# --- the Obsidian settings agree with what ships ---------------------------------------------------------------------
lock = json.loads((ROOT / "release/plugins.lock.json").read_text(encoding="utf-8"))
enabled = json.loads((ROOT / ".obsidian/community-plugins.json").read_text(encoding="utf-8"))
check("community-plugins.json turns on exactly the bundled plugins", sorted(enabled) == sorted(p["id"] for p in lock["plugins"]),
      sorted(set(enabled) ^ {p["id"] for p in lock["plugins"]}))
appearance = json.loads((ROOT / ".obsidian/appearance.json").read_text(encoding="utf-8"))
check("appearance.json sets the bundled theme", appearance.get("cssTheme") == lock["theme"]["name"], appearance.get("cssTheme"))
tpl = json.loads((ROOT / ".obsidian/templates.json").read_text(encoding="utf-8"))
check("Obsidian's Templates points at _System/Templates", tpl.get("folder") == "_System/Templates", tpl)
core = json.loads((ROOT / ".obsidian/core-plugins.json").read_text(encoding="utf-8"))
check("core Templates is on", core.get("templates") is True)

# --- nothing in the download still speaks of what 3.0 removed --------------------------------------------------------
tracked = subprocess.run(["git", "-C", str(ROOT), "ls-files"], capture_output=True, text=True, check=True).stdout.splitlines()
shipped = [f for f in tracked if not f.startswith(("tests/", "release/", ".github/")) and f not in (".gitignore", "SECURITY.md", ".icor-for-life/CHANGELOG.md")]
stale = re.compile(r"06 AI Team|AI Team Knowledge|\bGL-10\d\d\b|\bSOP-10\d\d\b|\bWS-10\d\d\b|Scaffold Check")
hits = []
for f in shipped:
    p = ROOT / f
    if p.suffix not in (".md", ".json", ".base"):
        continue
    if stale.search(p.read_text(encoding="utf-8", errors="ignore")):
        hits.append(f)
check("no shipped note or setting mentions 06 AI Team, a GL, an SOP or Scaffold Check", not hits, hits[:10])
check("nothing tracked under 06 AI Team", not any(f.startswith("06 AI Team/") for f in tracked))
check("no .env, data.json or plugin folder tracked", not any(re.search(r"(^|/)\.env$|data\.json$|^\.obsidian/(plugins|themes)/", f) for f in tracked))

print(f"OK {checks} cases held" if not fails else f"FAIL {len(fails)} of {checks} cases")
sys.exit(1 if fails else 0)
