#!/usr/bin/env python3
"""migrate-to-3.py: brings an ICOR for Life 2.x folder (or an early 3.0 one) to the 3.0 layout, from a 3.0 download.

    python3 "<3.0 download>/_System/Tools/migrate-to-3.py" "<your folder>"            what it would do (changes nothing)
    python3 "<3.0 download>/_System/Tools/migrate-to-3.py" "<your folder>" --live     do it

    --plugins     also add the plugins your folder does not have yet (Journal, Objects…) and turn them on
    --sources     also turn reference notes in 04 Notes into sources in 06 Sources
    --move-env    also copy 06 AI Team/AI Team Knowledge/.env to .icor-for-life/.env (the plugins read both)

The numbered folders follow the ICOR stages (Input 00 Daily Notes, 01 Inbox; Control 02 My Life, 03 Journal, 04 Notes,
05 Contacts, 06 Sources; Output 07 Planner, 08 Workbench; Refine 09 AI; then 10 Files and 11 Databases): the old folders
are moved to these (the Inner World's folders come up one level), and the paths written in your notes, bases, canvases
and Obsidian settings follow. A myPKA team's files (06 AI Team, .mypka) are left as they are.

It never deletes and never overwrites a file you have: where 3.0 has a different version of a file you already have,
the new one lands beside yours as <file>.update. 06 AI Team stays where it is; when no AI team lives in it you can
delete it yourself once you are happy. A folder with a myPKA team (AGENTS.md, .mypka/) keeps its team untouched:
the 3.0 AGENTS.md lands as AGENTS.icor-for-life.md beside the team's own.
"""
import argparse, json, re, shutil, sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
NEW = HERE.parents[1]          # the 3.0 download this script came with
MARK = "# AGENTS.md: how this folder works"


# The folders, old path → new path, in the order they move. Matched by full name, never by number: a 2.x folder may
# still hold 06 AI Team, and 06 is Sources now. Two layouts come here: 2.x (00 Daily Scratchpad … 07 Databases) and the
# first 3.0 one (02 Inner World, 03 Outer World, 04 Assets, 05 Databases, 06 Planner; Tom 2026-11-23). The Workbench
# layout (Tom 2026-11-28) lifts the Inner World's folders to the top and gives the Workbench and the AI their own.
MOVES = []
for inner in ("04 Inner World", "02 Inner World"):
    MOVES += [(f"{inner}/My Life", "02 My Life"), (f"{inner}/Journal", "03 Journal"), (f"{inner}/Notes", "04 Notes"),
              (f"{inner}/Contacts", "05 Contacts"), (f"{inner}/Meetings", "04 Notes/Meetings"),
              (f"{inner}/ICOR Journey Notes", "04 Notes/ICOR Journey Notes")]
MOVES += [("00 Daily Scratchpad", "00 Daily Notes"), ("06 Outer World", "06 Sources"), ("03 Outer World", "06 Sources"),
          ("02 Planner", "07 Planner"), ("06 Planner", "07 Planner"), ("05 Assets", "10 Files"), ("04 Assets", "10 Files"),
          ("07 Databases", "11 Databases"), ("05 Databases", "11 Databases")]
INNER = ("04 Inner World", "02 Inner World")      # what is left in them afterwards goes to 04 Notes/<folder>
STAGE_FOLDERS = dict(MOVES)                       # old path → new path (at() and the tests read it)


def path_rx(mapping):
    keys = sorted(mapping, key=len, reverse=True)
    return re.compile(r"(?<![\w-])(" + "|".join(re.escape(k) for k in keys) + r")(?![\w-])")


REWRITE = {".md", ".base", ".canvas", ".json"}
KEEP_OUT = {".git", ".trash", "node_modules", "06 AI Team", ".mypka"}


def path_files(root: Path):
    """The files whose text may name a folder: notes, bases, canvases, Obsidian's settings and each plugin's data.json
    (never a plugin's code), and nothing of a myPKA team."""
    for p in root.rglob("*"):
        rel = p.relative_to(root)
        if not p.is_file() or p.suffix not in REWRITE or KEEP_OUT & set(rel.parts):
            continue
        if rel.parts[0] == ".obsidian" and len(rel.parts) > 2 and rel.parts[1] == "plugins" and p.name != "data.json":
            continue
        yield p


def rename_stages(plan, old: Path):
    """Step 0: the folders move to the 3.0 layout; then every written path follows."""
    moves, taken, tidies = [], set(), []
    already = [(was, now) for was, now in MOVES if not (old / was).exists() and (old / now).is_dir()]
    for was, now in MOVES:
        if not (old / was).is_dir():
            continue
        if now in taken:
            plan.note(f"{was} is left as it is: {now} comes from another folder. Move what is in it into {now} yourself.")
            continue
        if (old / now).exists():
            plan.note(f"Both {was} and {now} exist: {was} is left as it is. Move what is in it into {now} yourself.")
            continue
        moves.append((was, now))
        taken.add(now)
    def move(was, now):
        (old / now).parent.mkdir(parents=True, exist_ok=True)
        (old / was).rename(old / now)
    for was, now in moves:
        plan.do(f"folder {was} → {now}", lambda was=was, now=now: move(was, now))
    # What is left in an Inner World: its own folders go to 04 Notes/<name>, its loose files (the old README) to a backup
    moved_from = {w for w, _ in moves}
    for inner in INNER:
        root = old / inner
        if not root.is_dir() or not any(w.startswith(inner + "/") for w in moved_from):
            continue
        for child in sorted(root.iterdir()):
            rel = f"{inner}/{child.name}"
            if rel in moved_from or child.name == ".DS_Store":
                continue
            if child.is_dir():
                now = f"04 Notes/{child.name}"
                if (old / now).exists() or now in taken:
                    plan.note(f"{rel} is left where it is: 04 Notes already has a {child.name} folder.")
                    continue
                moves.append((rel, now))
                taken.add(now)
                plan.do(f"folder {rel} → {now}", lambda rel=rel, now=now: move(rel, now))
            else:
                keep = old / ".icor-for-life/backups/migrate-to-3" / inner / child.name
                def stash(child=child, keep=keep):
                    keep.parent.mkdir(parents=True, exist_ok=True)
                    child.rename(keep)
                plan.do(f"{rel} → {keep.relative_to(old)} (kept, not deleted)", stash)
        def tidy(root=root, inner=inner):
            try:
                ds = root / ".DS_Store"
                if ds.is_file():
                    ds.unlink()
                if root.is_dir() and not any(root.iterdir()):
                    root.rmdir()
            except OSError as e:
                print(f"      {inner} is left in place ({e.strerror}); it is empty, delete it yourself")
        tidies.append((f"the empty {inner} folder is removed", tidy))
    # A run that stopped part way (a folder that would not delete, a closed laptop) moved some folders already: their
    # paths still follow, so running again finishes the job.
    done = dict(already)
    done.update(moves)
    if not done:
        for text, fn in tidies:
            plan.do(text, fn)
        return
    for inner in INNER:
        if any(w.startswith(inner + "/") for w in done):
            done.setdefault(inner, "04 Notes")
    rx = path_rx(done)
    def rewrite():
        n = 0
        for p in path_files(old):
            try:
                text = p.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            new = rx.sub(lambda m: done[m.group(1)], text)
            if new != text:
                p.write_text(new, encoding="utf-8")
                n += 1
        print(f"      paths rewritten in {n} file(s)")
    plan.do("paths in notes, bases, canvases and Obsidian settings follow the new folder names", rewrite)
    for text, fn in tidies:
        plan.do(text, fn)


def at(old: Path, new_name: str) -> Path:
    """Where a folder is now: under its new name, or still under its old one (a dry run renames nothing)."""
    if (old / new_name).exists():
        return old / new_name
    was = next((k for k, v in MOVES if v == new_name and (old / k).exists()), None)
    return old / was if was else old / new_name


class Plan:
    def __init__(self, live):
        self.live, self.steps, self.notes = live, [], []

    def do(self, text, fn=None):
        self.steps.append(text)
        if self.live and fn:
            fn()

    def note(self, text):
        self.notes.append(text)


def same(a: Path, b: Path) -> bool:
    return a.is_file() and b.is_file() and a.read_bytes() == b.read_bytes()


def copy_tree(plan, src: Path, dst: Path, label: str):
    """Adds every file of src under dst: new files as they are, differing ones as <file>.update."""
    new = upd = 0
    for f in sorted(p for p in src.rglob("*") if p.is_file() and p.name != ".DS_Store"):
        to = dst / f.relative_to(src)
        if not to.exists():
            new += 1
            if plan.live:
                to.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, to)
        elif not same(f, to):
            upd += 1
            if plan.live:
                shutil.copy2(f, to.with_name(to.name + ".update"))
    if new or upd:
        plan.do(f"{label}: {new} new file(s){f', {upd} beside yours as .update' if upd else ''}")
    return new, upd


def frontmatter(text):
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---\n", 4)
    return (text[4:end], text[end + 5:]) if end > 0 else (None, text)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("folder")
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--plugins", action="store_true")
    ap.add_argument("--sources", action="store_true")
    ap.add_argument("--move-env", action="store_true")
    a = ap.parse_args()
    old = Path(a.folder).expanduser().resolve()
    if not any((old / d).is_dir() for d in ("02 My Life", "04 Notes", "02 Inner World", "04 Inner World")):
        sys.exit(f"FAIL {old} does not look like an ICOR for Life folder (no My Life, no Inner World)")
    if old == NEW:
        sys.exit("FAIL that is the 3.0 download itself; give the folder you want to bring to 3.0")
    version = (old / ".icor-for-life/VERSION").read_text().strip() if (old / ".icor-for-life/VERSION").is_file() else "unknown"
    if version.startswith("3.") and not any((old / k).is_dir() for k, _ in MOVES) and all(
            (old / f).is_dir() for f in ("08 Workbench", "09 AI/Skills")) and not (old / "_System/Skills").exists() \
            and (old / "AboutMe.md").is_file():
        sys.exit(f"OK {old.name} is already {version}")
    agents = old / "AGENTS.md"
    team = (old / ".mypka").is_dir() or (agents.is_file() and MARK not in agents.read_text(encoding="utf-8", errors="ignore"))
    plan = Plan(a.live)
    print(f"{'Bringing' if a.live else 'Would bring'} {old} (ICOR for Life {version}{', with a myPKA team' if team else ''}) to 3.0\n")

    # 0. the folders follow the ICOR stages
    rename_stages(plan, old)
    # 1. what every device needs; the skills moved from _System/Skills to 09 AI/Skills (2026-11-28), with any change of yours
    if (old / "_System/Skills").is_dir() and not (old / "09 AI/Skills").exists():
        def move_skills():
            (old / "09 AI").mkdir(exist_ok=True)
            shutil.move(str(old / "_System/Skills"), str(old / "09 AI/Skills"))
        plan.do("_System/Skills → 09 AI/Skills (the skills live with your AI now)", move_skills)
    elif (old / "_System/Skills").is_dir():
        plan.note("Both _System/Skills and 09 AI/Skills are there. 09 AI/Skills is the one AI tools get; "
                  "move anything of yours from _System/Skills into it and delete _System/Skills.")
    copy_tree(plan, NEW / "_System", old / "_System", "_System (schema, templates, tools)")
    # 2. the Outer World, the Workbench and the AI's folder
    copy_tree(plan, NEW / "06 Sources", at(old, "06 Sources"), "06 Sources (README, Web Clipper template, Readwise, Sources.base)")
    copy_tree(plan, NEW / "08 Workbench", old / "08 Workbench", "08 Workbench (where you work)")
    copy_tree(plan, NEW / "09 AI", old / "09 AI", "09 AI (your AI's skills, memory, log and weekly reviews)")
    if not (old / "AboutMe.md").exists():
        plan.do("AboutMe.md (who you are, for your AI: fill it in)", lambda: shutil.copy2(NEW / "AboutMe.md", old / "AboutMe.md"))
    # 3. how any AI reads the folder
    if team:
        copy_tree_file = NEW / "AGENTS.md"
        plan.do("AGENTS.icor-for-life.md beside your team's AGENTS.md (your team keeps its own)",
                lambda: shutil.copy2(copy_tree_file, old / "AGENTS.icor-for-life.md"))
        plan.note("Your myPKA team's AGENTS.md is untouched. To give your agents the 3.0 rules, add one line to it: "
                  "\"Read AGENTS.icor-for-life.md for how the ICOR for Life folders work.\"")
    elif not agents.exists():
        plan.do("AGENTS.md (how the folder works, for any AI)", lambda: shutil.copy2(NEW / "AGENTS.md", agents))
    elif not same(NEW / "AGENTS.md", agents):
        plan.do("AGENTS.md.update beside yours", lambda: shutil.copy2(NEW / "AGENTS.md", old / "AGENTS.md.update"))
    if (old / "CLAUDE.md").exists() and not team:
        plan.note("Your folder has a CLAUDE.md. Claude Code reads AGENTS.md only when there is no CLAUDE.md: "
                  "add the line @AGENTS.md to your CLAUDE.md, or remove it if it holds nothing of yours.")
    for target in (".agents/skills", ".claude/skills"):
        copy_tree(plan, NEW / "09 AI/Skills", old / target, f"{target} (the skills, where AI tools look)")

    # 4. Obsidian: Templates points at _System/Templates
    obs = old / ".obsidian"
    if obs.is_dir():
        tj = obs / "templates.json"
        cur = json.loads(tj.read_text()) if tj.is_file() else {}
        if cur.get("folder") != "_System/Templates":
            def set_templates():
                cur["folder"] = "_System/Templates"
                tj.write_text(json.dumps(cur, indent=2))
                cp = obs / "core-plugins.json"
                if cp.is_file():
                    core = json.loads(cp.read_text())
                    if isinstance(core, dict):
                        core["templates"] = True
                        cp.write_text(json.dumps(core, indent=2))
            plan.do(f"Obsidian's Templates: {cur.get('folder') or 'not set'} → _System/Templates", set_templates)
        # 5. plugins the folder does not have yet
        if a.plugins:
            have = set(p.name for p in (obs / "plugins").iterdir()) if (obs / "plugins").is_dir() else set()
            cpj = obs / "community-plugins.json"
            enabled = json.loads(cpj.read_text()) if cpj.is_file() else []
            bundled = NEW / ".obsidian/plugins"
            for p in sorted(bundled.iterdir()) if bundled.is_dir() else []:
                if p.name in have:
                    continue
                def add(p=p):
                    shutil.copytree(p, obs / "plugins" / p.name)
                    if p.name not in enabled:
                        enabled.append(p.name)
                        cpj.write_text(json.dumps(enabled, indent=2))
                plan.do(f"plugin {p.name} added and turned on", add)
            if (obs / "plugins/icor-for-life-scaffold-check").is_dir():
                plan.note("Scaffold Check is retired: turn it off in Settings, Community plugins, and remove it when you like.")
            plan.note("Plugins you already have stay as they are: update them in Settings, Community plugins, Check for updates.")
    else:
        plan.note("No .obsidian folder here: open the folder in Obsidian once to get its settings, then run this again for them.")

    # 6. the shared keys
    env_old, env_new = old / "06 AI Team/AI Team Knowledge/.env", old / ".icor-for-life/.env"
    if env_old.is_file() and not env_new.exists():
        if a.move_env:
            def move_env():
                env_new.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(env_old, env_new)
            plan.do(".env copied to .icor-for-life/.env (the old file stays; delete it when the plugins work)", move_env)
        else:
            plan.note("Your plugins' keys are in 06 AI Team/AI Team Knowledge/.env. The plugins still read them there; "
                      "run again with --move-env to copy them to .icor-for-life/.env.")

    # 7. reference notes → sources
    notes = at(old, "04 Notes")
    refs = []
    for f in sorted(notes.rglob("*.md")) if notes.is_dir() else []:
        fm, _ = frontmatter(f.read_text(encoding="utf-8", errors="ignore"))
        if fm and re.search(r"^type:\s*note\s*$", fm, re.M) and re.search(r"^note_type:\s*reference\s*$", fm, re.M):
            refs.append(f)
    if refs and a.sources:
        for f in refs:
            to = at(old, "06 Sources") / f.name
            if to.exists():
                plan.note(f"{f.name} is already in 06 Sources; left in Notes.")
                continue
            def move(f=f, to=to):
                text = f.read_text(encoding="utf-8")
                fm, body = frontmatter(text)
                kind = "article" if re.search(r"^source_url:\s*\S", fm, re.M) else "other"
                fm = re.sub(r"^type:\s*note\s*$", "type: source", fm, flags=re.M)
                fm = re.sub(r"^note_type:\s*reference\s*$", f"source_type: {kind}", fm, flags=re.M)
                to.parent.mkdir(parents=True, exist_ok=True)
                to.write_text(f"---\n{fm}\n---\n{body}", encoding="utf-8")
                f.unlink()
            plan.do(f"source: {f.relative_to(old)} → 06 Sources/{f.name}", move)
        plan.note("Links to the moved sources keep working: Obsidian finds a note by its name.")
    elif refs:
        plan.note(f"{len(refs)} reference note(s) in 04 Notes. Run again with --sources to make them sources "
                  "in 06 Sources.")
    inbox = old / "01 Inbox/Outer World"
    if inbox.is_dir() and any(p.suffix == ".md" and p.name != "README.md" and "archive" not in p.parts for p in inbox.rglob("*.md")):
        plan.note("01 Inbox/Outer World still holds clips: process them (skill process-outer-world), then the folder can go.")

    # 8. the version
    def bump():
        vf = old / ".icor-for-life/VERSION"
        vf.parent.mkdir(parents=True, exist_ok=True)
        if vf.is_file():
            shutil.copy2(vf, vf.with_name("VERSION.before-3"))
        vf.write_text((NEW / ".icor-for-life/VERSION").read_text())
    plan.do(f"version {version} → {(NEW / '.icor-for-life/VERSION').read_text().strip()}", bump)

    if (old / "03 WiP").is_dir():
        plan.note("03 WiP is not part of 3.0: work in progress lives in 08 Workbench now, one dated folder per piece of "
                  "work. Your 03 WiP is untouched; move what is still going into 08 Workbench, file what is finished.")
    if (old / "06 AI Team").is_dir():
        plan.note("06 AI Team is untouched. " + ("Your myPKA team lives there; keep it." if team else
                  "No AI team lives there: once you are happy with 3.0, you can delete it (its templates and tools are in _System now; "
                  "your AI keeps its log and memory in 09 AI)."))

    for i, s in enumerate(plan.steps, 1):
        print(f"  {i:2}. {s}")
    if plan.notes:
        print("\nFor you:")
        for n in plan.notes:
            print(f"  - {n}")
    if a.live:
        log = old / ".icor-for-life/migrate-to-3.log"
        log.parent.mkdir(parents=True, exist_ok=True)
        log.write_text("\n".join(plan.steps + [""] + plan.notes) + "\n", encoding="utf-8")
        print(f"\nOK done; the list is in {log.relative_to(old)}")
    else:
        print("\nOK nothing changed. Run again with --live to do it.")


if __name__ == "__main__":
    main()
