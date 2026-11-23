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
for folder in schema["folders"]:
    check(f"folder exists: {folder}", (ROOT / folder).is_dir())

# --- the ICOR stages (Tom, 2026-11-23): flat folders, numbered in stage order, each in exactly one stage ------------
NEW = ["00 Daily Notes", "01 Inbox", "02 Inner World", "03 Outer World", "04 Assets", "05 Databases", "06 Planner"]
check("schema: the folders are the seven, in stage order", list(schema.get("folders", {})) == NEW, list(schema.get("folders", {})))
check("schema: no rooms key any more", "rooms" not in schema)
stages = schema.get("stages", {})
check("schema: four stages, Input Control Output Refine", list(stages) == ["input", "control", "output", "refine"], list(stages))
want = {"input": ("#5271FC", NEW[:2]), "control": ("#52F49A", NEW[2:6]), "output": ("#FD63FF", NEW[6:])}
for st, (colour, folders) in want.items():
    check(f"stage {st}: colour {colour}", stages.get(st, {}).get("color") == colour, stages.get(st))
    check(f"stage {st}: its folders", stages.get(st, {}).get("folders") == folders, stages.get(st))
check("stage refine has no folder", stages.get("refine", {}).get("folders") == [], stages.get("refine"))
check("schema: worlds are 02 and 03", schema.get("worlds") == {"inner": "02 Inner World", "outer": "03 Outer World"}, schema.get("worlds"))
dn = json.loads((ROOT / ".obsidian/daily-notes.json").read_text())
check("Daily notes opens 00 Daily Notes", dn.get("folder") == "00 Daily Notes", dn)
app = json.loads((ROOT / ".obsidian/app.json").read_text())
check("attachments go to 04 Assets/Images", app.get("attachmentFolderPath") == "04 Assets/Images", app)
OLD = re.compile(r"00 Daily Scratchpad|02 Planner|04 Inner World|05 Assets|06 Outer World|07 Databases")
tracked = subprocess.check_output(["git", "-C", str(ROOT), "ls-files"], text=True).splitlines()
stale = []
for f in tracked:
    p = ROOT / f
    if f in (".icor-for-life/CHANGELOG.md", "tests/test-vault.py") or "migrate" in f or not p.is_file():
        continue
    try:
        if OLD.search(p.read_text(encoding="utf-8")) or OLD.search(f):
            stale.append(f)
    except UnicodeDecodeError:
        pass
check("no old folder name anywhere (migrate-to-3 and the changelog excepted)", not stale, stale[:8])
WORD = re.compile(r"\brooms?\b", re.I)
said = [f for f in tracked if f.endswith(".md") and f != ".icor-for-life/CHANGELOG.md" and (ROOT / f).is_file()
        and WORD.search((ROOT / f).read_text(encoding="utf-8"))]
check("no member- or AI-facing page says room", not said, said)

# --- how notes are written (Tom, 2026-11-23): no hard wraps, no blank first line, no title heading ------------------
import importlib.util as _iu
_spec = _iu.spec_from_file_location("tidy", ROOT / "_System/Tools/tidy-markdown.py")
TIDY = _iu.module_from_spec(_spec); _spec.loader.exec_module(TIDY)
visible = [ROOT / f for f in tracked if f.endswith(".md") and not f.startswith((".icor-for-life/", "tests/", "release/", ".agents/", ".claude/"))
           and (ROOT / f).is_file()]
wrapped = [str(p.relative_to(ROOT)) for p in visible if TIDY.unwrap(p.read_text(encoding="utf-8"))[1]]
check("no visible page is hard-wrapped (one paragraph per line)", not wrapped, wrapped[:8])
untidy = [str(p.relative_to(ROOT)) for p in visible if TIDY.tidy_top(p.read_text(encoding="utf-8"), p.stem)[1]]
check("no note or template starts with a blank line or its own title", not untidy, untidy[:8])

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

# --- words members never see, and links that go somewhere --------------------------------------------------------
banned = re.compile(r"\bscaffold\b|local folder|full stack", re.I)
said = []
for f in shipped:
    p = ROOT / f
    if p.suffix in (".md", ".json", ".base") and f not in ("LICENSE.md", ".icor-for-life/THIRD-PARTY-NOTICES.md"):
        if banned.search(p.read_text(encoding="utf-8", errors="ignore")):
            said.append(f)
check('no shipped note says "scaffold", "local folder" or "full stack"', not said, said)
names = {Path(f).stem for f in tracked} | {Path(f).name for f in tracked}
broken = []
rooms = tuple(schema["folders"])
for f in shipped:
    if not f.endswith(".md") or not f.startswith(rooms):
        continue
    for link in re.findall(r"\[\[([^\]|#]+)", (ROOT / f).read_text(encoding="utf-8", errors="ignore")):
        target = link.strip().split("/")[-1]
        if target and target not in names and not target.startswith("<"):
            broken.append(f"{f} -> {link}")
check("every link in the notes goes to a note or file that exists", not broken, broken[:10])
untagged = [f for f in shipped if f.endswith(".md") and f.startswith(("02 Inner World/", "03 Outer World/"))
            and not f.endswith("README.md") and "example" not in (ROOT / f).read_text(encoding="utf-8")]
check("every example note is tagged example, so a member knows what to delete", not untagged, untagged)

print(f"OK {checks} cases held" if not fails else f"FAIL {len(fails)} of {checks} cases")
sys.exit(1 if fails else 0)
