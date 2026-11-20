#!/usr/bin/env python3
"""migrate-to-3.py: brings an ICOR for Life 2.x folder to the 3.0 layout, from a 3.0 download.

    python3 "<3.0 download>/_System/Tools/migrate-to-3.py" "<your folder>"            what it would do (changes nothing)
    python3 "<3.0 download>/_System/Tools/migrate-to-3.py" "<your folder>" --live     do it

    --plugins     also add the plugins your folder does not have yet (Journal, Objects…) and turn them on
    --sources     also turn reference notes in 04 Inner World/Notes into sources in 06 Outer World
    --move-env    also copy 06 AI Team/AI Team Knowledge/.env to .icor-for-life/.env (the plugins read both)

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
    if not (old / "04 Inner World").is_dir():
        sys.exit(f"FAIL {old} does not look like an ICOR for Life folder (no 04 Inner World)")
    if old == NEW:
        sys.exit("FAIL that is the 3.0 download itself; give the folder you want to bring to 3.0")
    version = (old / ".icor-for-life/VERSION").read_text().strip() if (old / ".icor-for-life/VERSION").is_file() else "unknown"
    if version.startswith("3."):
        sys.exit(f"OK {old.name} is already {version}")
    agents = old / "AGENTS.md"
    team = (old / ".mypka").is_dir() or (agents.is_file() and MARK not in agents.read_text(encoding="utf-8", errors="ignore"))
    plan = Plan(a.live)
    print(f"{'Bringing' if a.live else 'Would bring'} {old} (ICOR for Life {version}{', with a myPKA team' if team else ''}) to 3.0\n")

    # 1. what every device needs
    copy_tree(plan, NEW / "_System", old / "_System", "_System (schema, templates, skills, tools)")
    # 2. the Outer World
    copy_tree(plan, NEW / "06 Outer World", old / "06 Outer World", "06 Outer World (README, Web Clipper template, Readwise, Sources.base)")
    # 3. how any AI reads the folder
    if team:
        copy_tree_file = NEW / "AGENTS.md"
        plan.do("AGENTS.icor-for-life.md beside your team's AGENTS.md (your team keeps its own)",
                lambda: shutil.copy2(copy_tree_file, old / "AGENTS.icor-for-life.md"))
        plan.note("Your myPKA team's AGENTS.md is untouched. To give your agents the 3.0 rules, add one line to it: "
                  "\"Read AGENTS.icor-for-life.md for how the ICOR for Life rooms work.\"")
    elif not agents.exists():
        plan.do("AGENTS.md (how the folder works, for any AI)", lambda: shutil.copy2(NEW / "AGENTS.md", agents))
    elif not same(NEW / "AGENTS.md", agents):
        plan.do("AGENTS.md.update beside yours", lambda: shutil.copy2(NEW / "AGENTS.md", old / "AGENTS.md.update"))
    if not (old / "CLAUDE.md").exists() and not team:
        plan.do("CLAUDE.md (points Claude Code to AGENTS.md)", lambda: shutil.copy2(NEW / "CLAUDE.md", old / "CLAUDE.md"))
    for target in (".agents/skills", ".claude/skills"):
        copy_tree(plan, NEW / "_System/Skills", old / target, f"{target} (the skills, where AI tools look)")

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
    notes = old / "04 Inner World/Notes"
    refs = []
    for f in sorted(notes.rglob("*.md")) if notes.is_dir() else []:
        fm, _ = frontmatter(f.read_text(encoding="utf-8", errors="ignore"))
        if fm and re.search(r"^type:\s*note\s*$", fm, re.M) and re.search(r"^note_type:\s*reference\s*$", fm, re.M):
            refs.append(f)
    if refs and a.sources:
        for f in refs:
            to = old / "06 Outer World" / f.name
            if to.exists():
                plan.note(f"{f.name} is already in 06 Outer World; left in Notes.")
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
            plan.do(f"source: {f.relative_to(old)} → 06 Outer World/{f.name}", move)
        plan.note("Links to the moved sources keep working: Obsidian finds a note by its name.")
    elif refs:
        plan.note(f"{len(refs)} reference note(s) in 04 Inner World/Notes. Run again with --sources to make them sources "
                  "in 06 Outer World.")
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

    if (old / "06 AI Team").is_dir():
        plan.note("06 AI Team is untouched. " + ("Your myPKA team lives there; keep it." if team else
                  "No AI team lives there: once you are happy with 3.0, you can delete it (its templates and tools are in _System now)."))

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
