#!/usr/bin/env python3
"""build-zip.py: builds the ICOR for Life download from the committed tree.

    python3 release/build-zip.py            a release: every plugin from its GitHub release
    python3 release/build-zip.py --local    local testing: plugins may come from local builds (the zip says -local)
    options: --out <dir> (default release/dist), --unzip-to <dir> (also unpack it there, for Obsidian)

What it does, in order:
  1. the tree is `git archive HEAD`: committed files only, so nothing uncommitted or ignored can reach a member;
  2. what belongs to the repository stays out: tests/, release/, .github/, .gitignore, SECURITY.md;
  3. the skills are copied from 09 AI/Skills to .agents/skills and .claude/skills, where AI tools look;
  4. every plugin and the theme in release/plugins.lock.json is copied in, each file checked against its sha256;
  5. .icor-for-life/manifest.json describes every file of the download;
  6. the gates (below) must all hold, or nothing is written;
  7. the zip is deterministic: sorted entries, one timestamp (the commit's), no extra attributes.

The gates: one top folder; no .env, data.json, workspace-mobile.json, .DS_Store, __pycache__ or symlink anywhere; no
06 AI Team; nothing that looks like a key outside the plugins' own code; every turned-on plugin present with an id
that matches its folder; the theme Obsidian is set to use is present; the schema parses; the skill copies are
identical to 09 AI/Skills; VERSION is the version in the file name.
"""
import argparse, hashlib, io, json, os, re, shutil, subprocess, sys, tarfile, tempfile, zipfile
from pathlib import Path

sys.dont_write_bytecode = True
REPO = Path(__file__).resolve().parent.parent
TOP = "ICOR for Life"
REPO_ONLY = ["tests", "release", ".github", ".gitignore", "SECURITY.md"]
FORBIDDEN = re.compile(r"(^|/)(\.env|[^/]*\.env|data\.json|workspace-mobile\.json|\.DS_Store|__pycache__|\.git)(/|$)")
SECRET = re.compile(r"(sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{20,}|gho_[A-Za-z0-9]{20,}|xox[bp]-[A-Za-z0-9-]{10,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----)")
sha = lambda b: hashlib.sha256(b).hexdigest()


def git(*args):
    return subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, check=True).stdout


def fetch(entry, kind, local_ok, cache):
    """The files of one plugin or the theme, checked against the lock."""
    src, out = entry["source"], {}
    if "local" in src:
        if not local_ok:
            raise SystemExit(f"BLOCKED {entry.get('id', entry.get('name'))} comes from a local build; a release takes GitHub releases only (or pass --local)")
        d = Path(src["local"])
        for f in entry["files"]:
            out[f] = (d / f).read_bytes()
    else:
        d = cache / (entry.get("id") or "theme") / entry["version"]
        d.mkdir(parents=True, exist_ok=True)
        missing = [f for f in entry["files"] if not (d / f).is_file()]
        if missing:
            subprocess.run(["gh", "release", "download", src["tag"], "-R", src["github"], "-D", str(d), "--clobber",
                            *sum((["-p", f] for f in missing), [])], check=True, capture_output=True)
        for f in entry["files"]:
            out[f] = (d / f).read_bytes()
    for f, want in entry["files"].items():
        if sha(out[f]) != want:
            raise SystemExit(f"BLOCKED {kind} {entry.get('id', entry.get('name'))}: {f} is not the file the lock pins (sha256 differs)")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--local", action="store_true")
    ap.add_argument("--out", default=str(REPO / "release/dist"))
    ap.add_argument("--unzip-to")
    a = ap.parse_args()

    version = git("show", "HEAD:.icor-for-life/VERSION").decode().strip()
    commit = git("rev-parse", "--short", "HEAD").decode().strip()
    when = int(git("log", "-1", "--format=%ct").decode().strip())
    dirty = git("status", "--porcelain", "--untracked-files=no").decode().strip()
    lock = json.loads(git("show", "HEAD:release/plugins.lock.json"))
    name = f"icor-for-life-vault-{version}{'-local' if a.local else ''}.zip"
    print(f"==> ICOR for Life {version} ({commit}){' with uncommitted changes left out' if dirty else ''}")

    with tempfile.TemporaryDirectory() as tmp:
        stage = Path(tmp) / TOP
        stage.mkdir()
        # 1. the committed tree
        with tarfile.open(fileobj=io.BytesIO(git("archive", "--format=tar", "HEAD"))) as t:
            try:
                t.extractall(stage, filter="data")
            except TypeError:  # Python before 3.12 without the backport: git's own archive, so the plain extract is safe
                t.extractall(stage)
        # 2. what stays in the repository
        for p in REPO_ONLY:
            q = stage / p
            if q.is_dir(): shutil.rmtree(q)
            elif q.exists(): q.unlink()
        # 3. the skill copies
        for target in (".agents/skills", ".claude/skills"):
            shutil.copytree(stage / "09 AI/Skills", stage / target)
        # 4. plugins and theme
        cache = REPO / "release/.cache"
        for p in lock["plugins"]:
            d = stage / ".obsidian/plugins" / p["id"]
            d.mkdir(parents=True)
            for f, b in fetch(p, "plugin", a.local, cache).items():
                (d / f).write_bytes(b)
            print(f"    plugin {p['id']} {p['version']} ({'local' if 'local' in p['source'] else 'GitHub release'})")
        th = lock["theme"]
        d = stage / ".obsidian/themes" / th["name"]
        d.mkdir(parents=True)
        for f, b in fetch(th, "theme", a.local, cache).items():
            (d / f).write_bytes(b)
        print(f"    theme {th['name']} {th['version']} ({'local' if 'local' in th['source'] else 'GitHub release'})")

        # 6. the gates
        fail = []
        files = sorted(p for p in stage.rglob("*") if p.is_file() or p.is_symlink())
        rel = lambda p: p.relative_to(stage).as_posix()
        for p in stage.rglob("*"):
            if p.is_symlink(): fail.append(f"symlink: {rel(p)}")
            if FORBIDDEN.search(rel(p)): fail.append(f"must not ship: {rel(p)}")
        if (stage / "06 AI Team").exists(): fail.append("06 AI Team is in the tree")
        for p in files:
            r = rel(p)
            if r.startswith(".obsidian/plugins/") or r.startswith(".obsidian/themes/") or p.suffix in (".jpg", ".png", ".webp"):
                continue
            m = SECRET.search(p.read_text(encoding="utf-8", errors="ignore"))
            if m: fail.append(f"looks like a key in {r}: {m.group(0)[:12]}…")
        enabled = json.loads((stage / ".obsidian/community-plugins.json").read_text())
        for pid in enabled:
            mf = stage / ".obsidian/plugins" / pid / "manifest.json"
            if not mf.is_file() or not (mf.parent / "main.js").is_file(): fail.append(f"{pid} is turned on but not bundled")
            elif json.loads(mf.read_text())["id"] != pid: fail.append(f"{pid}: its manifest names another id")
        theme = json.loads((stage / ".obsidian/appearance.json").read_text()).get("cssTheme")
        if theme and not (stage / ".obsidian/themes" / theme / "theme.css").is_file(): fail.append(f"the theme {theme} is set but not bundled")
        try: json.loads((stage / "_System/schema.json").read_text())
        except Exception as e: fail.append(f"_System/schema.json does not parse: {e}")
        src_sk = {rel(p)[len("09 AI/Skills/"):]: p.read_bytes() for p in (stage / "09 AI/Skills").rglob("*") if p.is_file()}
        for target in (".agents/skills", ".claude/skills"):
            got = {p.relative_to(stage / target).as_posix(): p.read_bytes() for p in (stage / target).rglob("*") if p.is_file()}
            if got != src_sk: fail.append(f"{target} differs from 09 AI/Skills")
        if (stage / ".icor-for-life/VERSION").read_text().strip() != version: fail.append("VERSION disagrees")
        if fail:
            print("\n".join("BLOCKED " + f for f in fail))
            raise SystemExit(1)
        print(f"    gates: {len(files)} files, all held")

        # 5. the manifest (after the gates, so it describes exactly what ships)
        manifest = {"name": "ICOR for Life", "version": version, "commit": commit, "local": a.local,
                    "plugins": {p["id"]: p["version"] for p in lock["plugins"]}, "theme": {th["name"]: th["version"]},
                    "files": {rel(p): sha(p.read_bytes()) for p in files}}
        (stage / ".icor-for-life/manifest.json").write_text(json.dumps(manifest, indent=1, sort_keys=True) + "\n")

        # 7. the zip
        out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
        zpath = out / name
        stamp = tuple(__import__("time").gmtime(when)[:6])
        entries = sorted(set([rel(p) for p in stage.rglob("*") if p.is_file()] + [rel(p) + "/" for p in stage.rglob("*") if p.is_dir()]))
        with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
            top = zipfile.ZipInfo(TOP + "/", stamp)
            top.external_attr = 0o40755 << 16   # without it, unzip makes the top folder unreadable (mode 000)
            z.writestr(top, b"")
            for e in entries:
                zi = zipfile.ZipInfo(f"{TOP}/{e}", stamp)
                if e.endswith("/"):
                    zi.external_attr = 0o40755 << 16
                    z.writestr(zi, b"")
                else:
                    zi.external_attr = 0o100644 << 16
                    zi.compress_type = zipfile.ZIP_DEFLATED
                    z.writestr(zi, (stage / e).read_bytes())
        if a.unzip_to:
            dest = Path(a.unzip_to)
            if (dest / TOP).exists(): shutil.rmtree(dest / TOP)
            dest.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(zpath) as z: z.extractall(dest)
            print(f"    unpacked to {dest / TOP}")
    b = zpath.read_bytes()
    print(f"OK {zpath} ({len(b) / 1e6:.1f} MB, sha256 {sha(b)})")


if __name__ == "__main__":
    main()
