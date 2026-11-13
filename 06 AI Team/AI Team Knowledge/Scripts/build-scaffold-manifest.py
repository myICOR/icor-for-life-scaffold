#!/usr/bin/env python3
"""Build .icor-for-life/manifest.json, the machine-readable description of
THIS version of the ICOR for Life Scaffold.

Usage:
  build-scaffold-manifest.py            -> (re)write .icor-for-life/manifest.json
  build-scaffold-manifest.py --check    -> exit 1 if the manifest on disk is stale
                                           or a removal has no changelog line,
                                           or a note has an empty name in it
  build-scaffold-manifest.py --check --upstream <myPKA checkout>
                                        -> also: every `vendored` file equals its
                                           upstream file in that checkout

THE SPLIT (plan step 12, 2026-09-24). This repo is the content half; myPKA
is the team half, and in mode A both are unpacked into one folder. What
changed here, and why:
  - VERSION may carry a pre-release tag (2.0.0-lab); tags, history and the
    changelog sections sort by semver precedence (2.0.0-lab < 2.0.0).
  - `files` is a map path -> sha256, the shape the updater (myPKA
    mypka-update.py) and the disjoint check read. The version folder is
    hashed too; the manifest's own entry is the literal "self".
  - `repo_only` holds the tracked files that never reach a member (the zip's
    RESIDUE_PATHS plus .gitignore, placement row 9), with their hashes.
  - `seed` lists shipped files that are the member's after the first install
    (.obsidian/workspace.json, which Obsidian rewrites, and since 2.3.0
    .obsidian/community-plugins.json, the member's own list of enabled
    plugins): the updater adds them when missing and never overwrites them.
    Formerly EXCLUDE.
  - `previous` maps a path to the sha256 of every older byte-state it had at
    an earlier tag: the updater overwrites only bytes a release shipped.
  - `previous_removed` (idea: Brian Carroll, @brijcarroll) is the same for
    the paths this release no longer ships: a path that `history` removes or
    renames away (not a move to myPKA) maps to the sha256 of every byte-state
    it had at an earlier tag that no `history` entry for it already names.
    `history` keeps only the last shipped hash, so without this an untouched
    copy of an older version reads as the member's own file. Only paths
    with such an extra hash are listed. A reader takes the union of this
    list and the path's `history` hashes; one that does not know the key
    ignores it and keeps its old answer.
  - NO `agents` list. The contracts live in myPKA now, and so does the list
    (build-mypka-manifest.py). Reading 06 AI Team/Agents from here found
    nothing in a sibling layout and a different product's files in mode A.
  - step 13 (Flint's step 14 preconditions, Marshall M2): `schema` is 2;
    `examples` lists the shipped example notes; a `history` removal that the
    myPKA manifest under --upstream ships is marked `moved_to: "mypka"` (with
    no --upstream the marks are carried from the manifest on disk) and needs
    no changelog line; `previous` holds only paths this release ships; tags
    may carry a leading v.
  - carried, never computed: name, implements, exposes, tools, vendored,
    source_commit, retired_ids. They are declared in the manifest by a person (step 3 and
    step 10) and kept across rebuilds; the tools and vendored paths are
    validated against `files`, and a vendored file's hash against its pin.

What the manifest is for. A member's vault is a copy of one version of this
repo with their own content grown on top. The Scaffold Check plugin reads the
manifest of the LATEST version and compares it with what the vault holds, so it
can tell the member three things a version number alone cannot:
  - which canonical files are missing, which they changed, and which changed
    upstream since they installed (three different answers, three different
    actions);
  - which files were REMOVED or MOVED upstream after their version and are
    still sitting in their vault (the CSS snippets that moved into the theme
    are the founding example);
  - whether the structure still holds: the rooms, the enabled plugins, every
    Base pointing at a folder that exists.

Everything in here is deterministic (GL-1005). The one piece of judgement, WHY
a file was removed and where it went, lives as prose in CHANGELOG.md; this
script only carries that line across into the manifest and refuses, under
--check, to describe a removal the changelog does not explain.

Sources of truth, none of them duplicated here:
  version   .icor-for-life/VERSION (one line, hand-bumped)
  rooms     the REQUIRED list in validate-scaffold.py (read via ast, not copied)
  plugins   .obsidian/community-plugins.json (the icor-for-life-* ids)
  snippets  .obsidian/appearance.json enabledCssSnippets
  files     `git ls-files`: every tracked file, shipped ones in `files`,
            the RESIDUE_PATHS the zip builder strips (read via regex from
            build-release-zip.sh, not copied) in `repo_only`
  history   `git diff --name-status -M` between consecutive tags
  previous  the blobs of the same paths at every earlier tag
  previous_removed  the blobs of the removed and renamed-away paths at
            every earlier tag, less the hashes `history` already holds
  notes     .icor-for-life/CHANGELOG.md, the line whose first backticked
            name is the exact path; never one with an empty name in it

Exit 0 = manifest written (or --check passed). Exit 1 = see stderr.
"""
import ast, datetime, hashlib, json, re, subprocess, sys
from pathlib import Path

# No .pyc into the tree this script hashes. It no longer imports a sibling
# (the agents reader moved to myPKA with the agents), and the switch stays so
# the next import cannot reintroduce the 1.24.0 CI defect.
sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
META = ROOT / ".icor-for-life"
MANIFEST = META / "manifest.json"
VERSION_FILE = META / "VERSION"
CHANGELOG = META / "CHANGELOG.md"
# schema 2 (Flint step 14, 4.1): `files` is a path map since the split, so
# the schema says so; a reader branches on `schema` first, shape second.
SCHEMA = 2

CHECK = "--check" in sys.argv[1:]
UPSTREAM = None
_args = sys.argv[1:]
if "--upstream" in _args:
    _i = _args.index("--upstream")
    if _i + 1 >= len(_args):
        sys.exit("FAIL --upstream needs the path of a myPKA checkout")
    UPSTREAM = Path(_args[_i + 1]).expanduser().resolve()
    del _args[_i:_i + 2]
_unknown = [a for a in _args if a != "--check"]
if _unknown:
    sys.exit("FAIL unknown argument(s): %s (usage: [--check] [--upstream <myPKA checkout>])" % " ".join(_unknown))
CARRIED = ("name", "implements", "exposes", "tools", "vendored", "source_commit", "retired_ids")
MANIFEST_REL = ".icor-for-life/manifest.json"
SEMVER = r"\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?"

def die(msg):
    sys.exit("FAIL " + msg)

def git(*args):
    r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        die("git %s: %s" % (" ".join(args), r.stderr.strip().splitlines()[-1] if r.stderr.strip() else "failed"))
    return r.stdout

# ----------------------------------------------------------------- version --
if not VERSION_FILE.is_file():
    die("%s is missing; write one line, e.g. 1.5.0" % VERSION_FILE.relative_to(ROOT))
version = VERSION_FILE.read_text(encoding="utf-8").strip()
if not re.fullmatch(SEMVER, version):
    die("VERSION must be MAJOR.MINOR.PATCH with an optional -pre-release tag, got %r" % version)

# -------------------------------------------------------------------- rooms --
# validate-scaffold.py owns the list of required folders. It runs on import,
# so read its source and lift the REQUIRED literal out of the syntax tree.
vs = (HERE / "validate-scaffold.py").read_text(encoding="utf-8")
rooms = None
for node in ast.parse(vs).body:
    if isinstance(node, ast.Assign) and any(getattr(t, "id", "") == "REQUIRED" for t in node.targets):
        rooms = ast.literal_eval(node.value)
if not rooms:
    die("could not find the REQUIRED list in validate-scaffold.py")

# ------------------------------------------------------- plugins, snippets --
try:
    enabled = json.loads((ROOT / ".obsidian/community-plugins.json").read_text(encoding="utf-8"))
except (OSError, ValueError) as exc:
    die("cannot read .obsidian/community-plugins.json: %s" % exc)
plugins = sorted(p for p in enabled if p.startswith("icor-for-life-"))
try:
    appearance = json.loads((ROOT / ".obsidian/appearance.json").read_text(encoding="utf-8"))
except (OSError, ValueError) as exc:
    die("cannot read .obsidian/appearance.json: %s" % exc)
snippets = sorted(appearance.get("enabledCssSnippets") or [])
theme = appearance.get("cssTheme") or ""

# -------------------------------------------------------------------- files --
# Since the split every tracked file is described: shipped ones in `files`,
# the rest in `repo_only`. Per-user state still ships (the first-open
# workspace), so it is listed, and marked SEED: the member's after the first
# install, never overwritten by the updater. .gitignore guards the repo and a
# mode A folder alike, and is never installed (placement row 9).
# community-plugins.json joined in 2.3.0, when the plugins stopped shipping:
# the download enables none (`[]`), and a member who updates keeps the
# plugins they installed and enabled. As a plain shipped file, an untouched
# copy of the 2.2.x list would have been overwritten with `[]`, switching
# every installed plugin off on the next open.
SEED = {".obsidian/workspace.json", ".obsidian/community-plugins.json"}
REPO_ONLY_ALWAYS = {".gitignore"}

# Files the zip builder's residue gate strips from the download never reach a
# member, so the manifest must not describe them either: the Scaffold Check
# plugin would report our build tooling as missing from every vault, and a
# member who "fixed" that would end up with a release workflow in their
# notes. The list is read out of the builder's RESIDUE_PATHS array, one
# quoted path per line, so there is exactly one list.
def residue_paths():
    src = (HERE / "build-release-zip.sh").read_text(encoding="utf-8")
    m = re.search(r"^declare -a RESIDUE_PATHS=\(\n(.*?)^\)", src, re.M | re.S)
    if not m:
        die("could not find the RESIDUE_PATHS array in build-release-zip.sh")
    paths = re.findall(r'^\s*"([^"]+)"\s*$', m.group(1), re.M)
    if not paths:
        die("the RESIDUE_PATHS array in build-release-zip.sh names no paths")
    return set(paths)

RESIDUE = residue_paths()

def kind_of(path):
    if path.endswith(".base"): return "base"
    if "/Guidelines/" in path: return "guideline"
    if "/SOPs/" in path: return "sop"
    if "/Workstreams/" in path: return "workstream"
    if "/Agents/" in path: return "agent"
    if "/Scripts/" in path: return "script"
    if "/Avatars/" in path or "/Brand/" in path: return "asset"
    if path.startswith(".obsidian/"): return "config"
    if path.startswith(".claude/"): return "claude"
    return "doc"

EXAMPLE_TAG = re.compile(r"^tags:.*\bexample\b|^\s*-\s*example\s*$", re.M)

def is_example(path, data):
    if not path.endswith(".md"): return False
    head = data[:2000].decode("utf-8", "ignore")
    if not head.startswith("---"): return False
    end = head.find("\n---", 3)
    return bool(EXAMPLE_TAG.search(head[:end] if end > 0 else head))

tracked = sorted(p for p in git("ls-files", "-z").split("\0") if p)
files, repo_only, examples = {}, {}, []
for p in tracked:
    if p == MANIFEST_REL:
        files[p] = "self"
        continue
    fp = ROOT / p
    if not fp.is_file():
        die("tracked but missing on disk: %s" % p)
    data = fp.read_bytes()
    h = hashlib.sha256(data).hexdigest()
    (repo_only if (p in RESIDUE or p in REPO_ONLY_ALWAYS) else files)[p] = h
    if p in files and is_example(p, data):
        examples.append(p)
seed = sorted(p for p in SEED if p in files)
# `examples` (Flint step 14, 4.2): the shipped example notes, the member's to
# delete. The 1.x list carried a per-file `example` flag; the map has no room.
examples = sorted(examples)

# -------------------------------------------------------------------- bases --
IN_FOLDER = re.compile(r'file\.inFolder\("([^"]+)"\)')
bases = []
for fpath in files:
    if kind_of(fpath) != "base": continue
    txt = (ROOT / fpath).read_text(encoding="utf-8", errors="ignore")
    bases.append({"path": fpath, "folders": sorted(set(IN_FOLDER.findall(txt)))})

# ------------------------------------------------------------------- agents --
# None here since the split: the contracts and their list live in myPKA
# (build-mypka-manifest.py). A checker must accept a manifest without them.

# ------------------------------------------------------------------ history --
# Machine facts from git: what each tagged version removed, renamed and added
# relative to the tag before it. HEAD counts as the version in VERSION when it
# sits past the newest tag, which is the state a manifest is built in.
def semver_key(t):
    """semver precedence: 2.0.0-lab < 2.0.0 < 2.0.1. None if not a version."""
    m = re.fullmatch(r"v?(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z.-]+))?", t or "")
    if not m:
        return None
    pre = m.group(4)
    ids = tuple((0, int(x), "") if x.isdigit() else (1, 0, x) for x in pre.split(".")) if pre else ()
    return (int(m.group(1)), int(m.group(2)), int(m.group(3)), 0 if pre else 1, ids)

tags = sorted((t for t in git("tag").split() if semver_key(t)), key=semver_key)
head_tag = git("describe", "--tags", "--exact-match", "HEAD").strip() if git("tag", "--points-at", "HEAD").strip() else ""
points = [(t, t) for t in tags]
if not head_tag:
    if tags and semver_key(version) <= semver_key(tags[-1]):
        die("VERSION %s is not newer than the latest tag %s, yet HEAD is untagged; bump VERSION" % (version, tags[-1]))
    points.append((version, "HEAD"))
elif semver_key(version) != semver_key(head_tag):
    # HEAD carries a tag, and VERSION names a different version. Neither the
    # tags nor the HEAD branch above will produce a history entry for VERSION,
    # so the manifest would be written claiming to describe a version whose own
    # history is missing. It passes --check here and fails in CI on a clean
    # checkout of the tag, which is the worst shape a gate can have: green on
    # the machine that wrote it, red on the machine that ships it.
    #
    # This is what a bump does before the commit lands: VERSION says 1.19.1
    # while HEAD is still the 1.19.0 commit. The cure is the order, not a
    # retry. (2026-09-11, after it cost a failed release run.)
    die("VERSION %s but HEAD is tagged %s, so this manifest would have no history entry for %s.\n"
        "       Build the manifest AFTER the commit that carries it:\n"
        "         1. make your changes and bump VERSION\n"
        "         2. git add -A && git commit\n"
        "         3. python3 build-scaffold-manifest.py     (HEAD is untagged here: correct)\n"
        "         4. git add -A && git commit --amend --no-edit\n"
        "         5. git tag %s && push both\n"
        "       Or, if the tag already exists, move it to the amended commit with git tag -f."
        % (version, head_tag, version, version))

def changelog_sections():
    """version -> the text of that version's section in CHANGELOG.md"""
    out = {}
    if not CHANGELOG.is_file(): return out
    cur = None
    for line in CHANGELOG.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^##\s+\[?(%s)\]?" % SEMVER, line)
        if m:
            cur = m.group(1); out[cur] = []
        elif cur:
            out[cur].append(line)
    return {k: "\n".join(v) for k, v in out.items()}

sections = changelog_sections()
TICKED = re.compile(r"`([^`]+)`")

def note_for(ver, path):
    """The changelog line whose SUBJECT is this exact path: its first
    backticked name. A line that names the path only in passing explains
    another file (the `CLAUDE.md` line mentions myPKA's `AGENTS.md`), so it
    is not this path's note. A line that opens with the path drops it, since
    the report shows the path beside the note ("`x` is deleted." gives "is
    deleted."); a line that names it later keeps it whole, so the note never
    reads with a hole where the name was ("Removed: , the Claude Code entry
    file", the 2.0.0 bug Felix found in Scaffold Check)."""
    tick = "`%s`" % path
    for line in sections.get(ver, "").splitlines():
        names = TICKED.findall(line)
        if not names or names[0] != path:
            continue
        text = line.strip().lstrip("-* ").strip()
        if text.startswith(tick):
            text = text[len(tick):].strip(" :-")
        return text
    return ""

# A note is shown to members as it is. One with an empty slot where a name
# belongs (it opens on punctuation, ": ," or "( )", a run of spaces, an empty
# pair of backticks) is refused, whoever made the hole: this builder, or a
# changelog line written "- `x`, removed." (its note would open ", removed.").
NOTE_HOLE = re.compile(r"^[,;:.)]|[:(]\s*[,;:.)]|\S {2,}\S|``")

def note_hole(note):
    return bool(note) and NOTE_HOLE.search(note) is not None

# moved_to (Flint step 14, 4.1): a removal that the pinned myPKA manifest
# ships is a MOVE, not a removal, and says so. With --upstream the builder
# reads that manifest and decides; without it the marks are carried from the
# manifest on disk for the same version and path (a build without the myPKA
# checkout neither adds nor drops one). A moved file needs no changelog line
# of its own: the move is its explanation.
try:
    on_disk = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.is_file() else {}
except ValueError as exc:
    die("manifest.json is not valid JSON: %s" % exc)
UP_FILES = None
if UPSTREAM is not None and (UPSTREAM / ".mypka/manifest.json").is_file():
    try:
        UP_FILES = set(json.loads((UPSTREAM / ".mypka/manifest.json").read_text(encoding="utf-8")).get("files") or {})
    except ValueError as exc:
        die("--upstream %s: .mypka/manifest.json is not valid JSON: %s" % (UPSTREAM, exc))
CARRIED_MOVES = {(h.get("version"), r.get("path")) for h in (on_disk.get("history") or [])
                 for r in (h.get("removed") or []) if r.get("moved_to") == "mypka"}

def moved(label, path):
    if UP_FILES is not None:
        return path in UP_FILES
    return (label, path) in CARRIED_MOVES

def removal(label, path, sha256, **extra):
    note = note_for(label, path)
    mv = moved(label, path)
    if not note and not mv:
        unexplained.append((label, path))
    if note_hole(note):
        holed.append((label, path, note))
    entry = {"path": path, "sha256": sha256, "note": note or ("moved to myPKA" if mv else "")}
    if mv:
        entry["moved_to"] = "mypka"
    entry.update(extra)
    return entry

unexplained = []
holed = []
history = []
prev = None
for label, rev in points:
    if prev is None:
        prev = rev; continue
    date = git("log", "-1", "--format=%cs", rev).strip()
    removed, renamed, added = [], [], []
    # Every removed or renamed entry carries the sha256 of the file AS IT WAS
    # at the previous version. The plugin matches leftovers by content, not by
    # name: a member's own GL-1001 that happens to share a name with a scaffold
    # file that was later renamed is theirs, and must not be reported as a
    # leftover. Only the scaffold's actual bytes are.
    def blob_sha(rev_, path):
        r = subprocess.run(["git", "show", "%s:%s" % (rev_, path)], cwd=ROOT, capture_output=True)
        return hashlib.sha256(r.stdout).hexdigest() if r.returncode == 0 else ""
    # The unreleased version is the INDEX, not HEAD: `files` above comes from
    # `git ls-files`, which reads the index, so a staged rename must show up
    # here too or the manifest would list GL-1001 as a file while its history
    # said nothing was renamed. Tagged versions are commits and diff as such.
    diff_args = ["diff", "--cached", "--name-status", "-M", prev] if rev == "HEAD" \
        else ["diff", "--name-status", "-M", prev, rev]
    seen_removed = set()
    for line in git(*diff_args).splitlines():
        parts = line.split("\t")
        code = parts[0][0]
        if code == "D":
            removed.append(removal(label, parts[1], blob_sha(prev, parts[1])))
            seen_removed.add(parts[1])
        elif code == "R":
            renamed.append({"from": parts[1], "to": parts[2], "from_sha256": blob_sha(prev, parts[1])})
        elif code == "A":
            added.append(parts[1])
    # The member download is built from main, not from a tag, so a file that
    # was added and deleted again BETWEEN two versions never shows in the
    # tag-to-tag diff and yet sits in every copy downloaded in between.
    # icor-scaffold.css lived on main for one day, 2026-08-31. Anything
    # deleted anywhere in the span, and absent at the end of it, is a removal
    # of this version too; its hash is the blob just before the deleting commit.
    span_end = "HEAD" if rev == "HEAD" else rev
    present_at_end = set(filter(None, (git("ls-files", "-z") if rev == "HEAD"
                                        else git("ls-tree", "-r", "--name-only", "-z", rev)).split("\0")))
    for path in sorted(set(filter(None, git("log", "--diff-filter=D", "--name-only", "--format=",
                                             "%s..%s" % (prev, span_end)).split("\n")))):
        if path in seen_removed or path in present_at_end: continue
        deleting = git("log", "-1", "--format=%H", "--diff-filter=D", "%s..%s" % (prev, span_end), "--", path).strip()
        removed.append(removal(label, path, blob_sha(deleting + "^", path) if deleting else "", transient=True))
    history.append({"version": label, "date": date, "removed": removed, "renamed": renamed, "added": added})
    prev = rev
history.reverse()  # newest first

# ----------------------------------------------------------------- previous --
# Every older byte-state a path had at an earlier tag. The updater overwrites
# a member's file only when its bytes are one a release shipped; without this
# it knows only the version the member installed, and one skipped release
# would turn every untouched file into "edited".
previous = {}
for tag in (t for t in tags if semver_key(t) < semver_key(version)):
    entries = []
    for rec in filter(None, git("ls-tree", "-r", "-z", "--full-tree", tag).split("\0")):
        info, path = rec.split("\t", 1)
        _mode, typ, oid = info.split()
        # Only paths this release still ships (Marshall M2): an older state
        # of a file ICOR no longer ships is nothing the updater can use.
        if typ == "blob" and path in files and path != MANIFEST_REL:
            entries.append((path, oid))
    if not entries:
        continue
    out = subprocess.run(["git", "cat-file", "--batch"], cwd=ROOT, capture_output=True,
                         input="".join(o + "\n" for _p, o in entries).encode()).stdout
    pos = 0
    for path, _oid in entries:
        nl = out.index(b"\n", pos)
        size = int(out[pos:nl].split()[2])
        h = hashlib.sha256(out[nl + 1:nl + 1 + size]).hexdigest()
        pos = nl + 1 + size + 1
        if files.get(path) != h:
            previous.setdefault(path, set()).add(h)
previous = {k: sorted(v) for k, v in sorted(previous.items())}

# --------------------------------------------------------- previous_removed --
# `previous` for the paths this release no longer ships (idea: Brian Carroll).
# A removal in `history` carries one hash, the bytes at the version before
# it; a member who never updated that file holds an OLDER state, which then
# matched nothing and was reported as their own work. Judged paths: removed
# without moving to myPKA (a move is judged by myPKA's manifest, whose
# `previous` holds the 1.x states), or renamed away. Kept small: a hash any
# `history` entry for the path already names is left out, and so is a path
# with nothing left. Tags only, the same evidence as `previous`.
named_in_history, judged = {}, set()
for h in history:
    for r in h["removed"]:
        named_in_history.setdefault(r["path"], set()).add(r["sha256"])
        if not r.get("moved_to"):
            judged.add(r["path"])
    for r in h["renamed"]:
        named_in_history.setdefault(r["from"], set()).add(r["from_sha256"])
        judged.add(r["from"])
judged = {p for p in judged if p not in files and p not in repo_only and p != MANIFEST_REL}
previous_removed, blob_hash = {}, {}
for tag in (t for t in tags if semver_key(t) < semver_key(version)):
    wanted = []
    for rec in filter(None, git("ls-tree", "-r", "-z", "--full-tree", tag).split("\0")):
        info, path = rec.split("\t", 1)
        _mode, typ, oid = info.split()
        if typ == "blob" and path in judged:
            wanted.append((path, oid))
    fresh = sorted({oid for _p, oid in wanted if oid not in blob_hash})
    if fresh:
        out = subprocess.run(["git", "cat-file", "--batch"], cwd=ROOT, capture_output=True,
                             input="".join(o + "\n" for o in fresh).encode()).stdout
        pos = 0
        for oid in fresh:
            nl = out.index(b"\n", pos)
            size = int(out[pos:nl].split()[2])
            blob_hash[oid] = hashlib.sha256(out[nl + 1:nl + 1 + size]).hexdigest()
            pos = nl + 1 + size + 1
    for path, oid in wanted:
        if blob_hash[oid] not in named_in_history[path]:
            previous_removed.setdefault(path, set()).add(blob_hash[oid])
previous_removed = {k: sorted(v) for k, v in sorted(previous_removed.items())}

# ------------------------------------------------------------------ carried --
carried = {k: on_disk[k] for k in CARRIED if k in on_disk}
carry_fails = []
# A RESIDUE_PATHS entry that is not tracked is stale: the zip builder's
# residue gate refuses it at release time ("expected to remove ... and it
# is not there"), after the tag exists. Refused here too, so Gate 1 sees it
# before any tag (2.0.0: release-gate-red-tests.sh moved to myPKA, the entry
# stayed). Same rule as build-mypka-manifest.py.
for p in sorted(RESIDUE - set(tracked)):
    carry_fails.append("RESIDUE_PATHS names %s, which is not tracked (a stale entry hides nothing, "
                       "and the zip builder's residue gate refuses it after the tag)" % p)
for tool, tpath in sorted((carried.get("tools") or {}).items()):
    if tpath not in files:
        carry_fails.append("tools.%s names %s, which this release does not ship" % (tool, tpath))
for vpath, pin in sorted((carried.get("vendored") or {}).items()):
    if vpath not in files:
        carry_fails.append("vendored %s is not a shipped file" % vpath)
    elif files[vpath] != pin.get("sha256"):
        carry_fails.append("vendored %s does not match its pin (a hand edit, or a sync that did not "
                           "rewrite the pin); edit upstream only" % vpath)
    if UPSTREAM is not None:
        up_rel = str(pin.get("upstream", "")).split(":", 1)[-1]
        up = UPSTREAM / up_rel
        if not up.is_file():
            carry_fails.append("vendored %s: upstream %s is not in %s" % (vpath, up_rel, UPSTREAM))
        elif hashlib.sha256(up.read_bytes()).hexdigest() != pin.get("sha256"):
            carry_fails.append("vendored %s: upstream %s in %s has moved on from the pin; sync the copy "
                               "and the pin together" % (vpath, up_rel, UPSTREAM))

manifest = {
    "schema": SCHEMA,
    "name": carried.get("name") or "ICOR for Life Scaffold",
    "version": version,
    "built": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "commit": git("rev-parse", "--short", "HEAD").strip(),
    "lab": ("lab" in version.split("-", 1)[1]) if "-" in version else False,
}
for k in ("source_commit", "implements", "exposes", "tools"):
    if k in carried:
        manifest[k] = carried[k]
manifest.update({
    "theme": theme,
    "rooms": rooms,
    "plugins": plugins,
    "snippets": snippets,
    "files": files,
    "repo_only": repo_only,
    "seed": seed,
    "examples": examples,
    "bases": bases,
    "history": history,
    "previous": previous,
    "previous_removed": previous_removed,
})
if "vendored" in carried:
    manifest["vendored"] = carried["vendored"]
# retired_ids: SOP/WS/GL numbers that were shipped once, or are reserved by
# code outside these repos, and never come back, declared by a person; check-disjoint.py counts them as used when it
# enforces "the next free number across both manifests".
if "retired_ids" in carried:
    manifest["retired_ids"] = carried["retired_ids"]

def holed_fails():
    return ["%s removes `%s` and its note has an empty name where a name belongs: %r; write the "
            "changelog line as \"- Removed: `%s`, what it was.\"" % (v, p, n, p) for v, p, n in holed]

# -------------------------------------------------------------------- check --
def strip_volatile(m):
    m = dict(m); m.pop("built", None); m.pop("commit", None); return m

if CHECK:
    fails = list(carry_fails)
    if not MANIFEST.is_file():
        fails.append("manifest.json does not exist; run build-scaffold-manifest.py")
    elif strip_volatile(on_disk) != strip_volatile(manifest):
        stale = sorted(k for k in set(on_disk) | set(manifest)
                       if k not in ("built", "commit") and on_disk.get(k) != manifest.get(k))
        fails.append("manifest.json is stale in: %s; the tree changed since it was built; "
                     "run build-scaffold-manifest.py" % ", ".join(stale))
    for ver, path in unexplained:
        fails.append("%s removes `%s` and CHANGELOG.md's %s section has no line naming it" % (ver, path, ver))
    fails += holed_fails()
    if not sections.get(version, "").strip():
        fails.append("CHANGELOG.md has no '## %s' section with content" % version)
    if fails:
        for f in fails: print("FAIL " + f, file=sys.stderr)
        sys.exit(1)
    print("OK manifest %s is current: %d files, %d repo-only, %d seed, %d bases, %d versions of history%s"
          % (version, len(files), len(repo_only), len(seed), len(bases), len(history),
             ", vendored pins match %s" % UPSTREAM if UPSTREAM else ""))
    sys.exit(0)

if carry_fails or holed:
    for f in carry_fails + holed_fails(): print("FAIL " + f, file=sys.stderr)
    die("nothing written")
META.mkdir(exist_ok=True)
MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("OK wrote %s: version %s, %d files, %d repo-only, %d seed, %d bases, %d versions of history"
      % (MANIFEST.relative_to(ROOT), version, len(files), len(repo_only), len(seed), len(bases), len(history)))
for ver, path in unexplained:
    print("WARN %s removes `%s` and CHANGELOG.md does not say why; --check will fail until it does" % (ver, path), file=sys.stderr)
