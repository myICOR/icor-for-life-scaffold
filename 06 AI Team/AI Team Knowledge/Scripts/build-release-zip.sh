#!/bin/bash
# Build a distribution zip of the ICOR for Life Scaffold that can NEVER
# contain personal data or API tokens, and can never contain an artifact
# whose version number disagrees with the bytes that number names.
#
# How safety is guaranteed:
#   1. The vault is never zipped directly. The scaffold content comes from
#      `git archive` of the scaffold repo: only tracked files ship, and
#      .env / workspace.json / plugin folders (whose data.json holds
#      tokens) are gitignored, so they cannot be tracked.
#   2. NO PLUGIN AND NO THEME SHIPS (2.3.0). The twelve ICOR for Life
#      plugins and the INKLINE theme are installed by the member from
#      Obsidian's community directory (Settings, Community plugins, Browse,
#      search "ICOR for Life"), and update there. The zip carries the vault
#      only. Until 2.2.2 this script staged them from their own repos and
#      releases and compared every byte with the published assets; all of
#      that went with the bundling.
#   3. A secret scan runs over the staged tree and aborts on any hit.
#   4. THE NO-BUNDLE GATE: the staged tree holds no .obsidian/plugins/ or
#      .obsidian/themes/ content and community-plugins.json enables
#      nothing, so a plugin folder committed by mistake, or a list that
#      enables a plugin the zip does not carry, blocks the build.
#   4b. THE NO-myPKA GATE (2.3.0): ICOR for Life is a content folder. The
#      agent team is myPKA 8, a separate download with its own folder, so
#      no myPKA file (AGENTS.md, .mypka/, the host folders, the team's
#      agents, SOPs, skills, tasks or session logs) may reach this zip, and
#      every staged file must be one this release's manifest describes.
#      This build needs no myPKA checkout either: the zipper and the
#      version-bump check sit beside this script, and the test gate runs
#      ICOR for Life's own suites.
#   5. THE RESIDUE GATE: this script and the release workflow that runs it
#      are our build tooling. They name our local mirror paths, our output
#      directory and our GitHub org, so they are a map of our internals and
#      they have no use to a member. Both are dropped from the staged tree
#      by exact path, and then an independent scan that knows nothing about
#      those paths fails the build if any of their fingerprints survive
#      anywhere in the tree. Removal alone would be silent filtering; the
#      scan is what makes a rename go red.
#      The zip is only written after every gate passes.
#   6. THE ZIP IS REPRODUCIBLE: every entry carries the staged commit's
#      timestamp and the entries are written in one fixed order, so the same
#      tag gives the same bytes. The release
#      workflow relies on this: a re-run compares its zip with the asset
#      already published under that version instead of overwriting it.
#      The zip itself is written by zip-staged-tree.sh, beside this script
#      (from myPKA until 2.3.0), a separate file so a test can build a
#      fixture twice under two locales and two clocks and assert one sha256.
#   7. NO GATE WRITES INTO THE BYTES IT IS CHECKING. Every gate that executes
#      code out of the staged tree runs against a COPY of it, and the staged
#      tree is hashed either side of that gate; a single changed or added byte
#      blocks the build. This is what 1.23.0 died of: the red-test gate
#      imports three Scripts modules with importlib, CPython wrote their
#      __pycache__/*.pyc into the staged tree, and a .pyc embeds the absolute
#      path of its source, which is a mktemp directory with six random
#      characters in its name. Three zip entries therefore changed on every
#      build. It was invisible on the maintainer's Mac, where Apple's
#      /usr/bin/python3 redirects the bytecode cache to
#      ~/Library/Caches/com.apple.python and nothing ever reached the tree.
#
# Why gate 4 exists. A member who opens the folder in Obsidian and finds a
# plugin enabled that the folder does not hold sees a "failed to load"
# notice on the first open; one who finds a stray plugin folder runs code
# nobody released. The plugins now reach a vault one way only, through the
# community directory, and this gate keeps it that way.
#
# Usage: bash build-release-zip.sh [output-dir]   (default: ~/Desktop)
#
# Environment (every one optional; the defaults are the local maintainer
# setup). MYPKA_TREE is no longer read (2.3.0): this build depends on no
# myPKA checkout.
#   ICOR_SCAFFOLD_TAG     stage this exact tag of the scaffold instead of
#                         origin/main. The release workflow sets it to the
#                         version it just tagged, so what ships is the tagged
#                         tree and nothing that landed on main after it. The
#                         tag must exist on the remote and its VERSION must
#                         equal the tag name.
#   ICOR_SCAFFOLD_GIT     the scaffold's bare mirror (default: the mirror
#                         ~/.icor-git/scaffold.git). Created if missing.
#   ICOR_SCAFFOLD_REMOTE  where that mirror fetches from (default: the public
#                         scaffold repository). A local dry run points both of
#                         these at a throwaway clone; CI never sets either.
#   ICOR_ZIP_DEBUG_DIR    write a listing of the staged tree (sha256 + path,
#                         one line per file) at three points, plus the finished
#                         zip's per-entry listing, into this directory. Nothing
#                         is read back and nothing is skipped because of it:
#                         like ICOR_ZIP_SELFTEST it can only ever ADD output,
#                         never turn a failing gate green. This exists because
#                         two zips of the same tag differed by two bytes on the
#                         CI runner while the same builder was byte-stable on
#                         the maintainer's Mac, and reasoning about which byte
#                         moved without holding both listings cost an hour.

set -euo pipefail

# The helper scripts this one calls live beside it, in the repo checkout, never
# in the staged tree: what archives the bytes must not be one of the bytes.
SELF_DIR="$(cd "$(dirname "$0")" && pwd)"
# The zipper is ICOR for Life's own since 2.3.0 (it came from myPKA, where
# it lived after the split). Repo-only: RESIDUE_PATHS strips it below.
ZIPPER="$SELF_DIR/zip-staged-tree.sh"
if [ ! -f "$ZIPPER" ]; then
  echo "RELEASE ABORTED: zip-staged-tree.sh is missing beside this script" >&2
  exit 1
fi

MIRRORS="$HOME/.icor-git"
SCAFFOLD_GIT="${ICOR_SCAFFOLD_GIT:-$MIRRORS/scaffold.git}"
SCAFFOLD_REMOTE="${ICOR_SCAFFOLD_REMOTE:-https://github.com/myICOR/icor-for-life-scaffold.git}"
SCAFFOLD_TAG="${ICOR_SCAFFOLD_TAG:-}"
OUT_DIR="${1:-$HOME/Desktop}"
STAMP="$(date +%Y-%m-%d)"
STAGE="$(mktemp -d /tmp/icor-release.XXXXXX)"
trap 'rm -rf "$STAGE"' EXIT
DEBUG_DIR="${ICOR_ZIP_DEBUG_DIR:-}"
[ -n "$DEBUG_DIR" ] && mkdir -p "$DEBUG_DIR"
# Scratch space for the builder's own bookkeeping. It sits OUTSIDE $STAGE on
# purpose: a file the builder writes into the tree it is about to ship is the
# exact defect this directory exists to detect.
WORK="$(mktemp -d /tmp/icor-release-work.XXXXXX)"
trap 'rm -rf "$STAGE" "$WORK"' EXIT

# Every `sort` and every `zip` in this script must order and stamp the same
# way on every machine, or the zip stops being a function of the commit. The
# individual call sites already say LC_ALL=C and TZ=UTC; setting both here as
# well means a call site that forgets cannot quietly reintroduce the defect.
export LC_ALL=C
export TZ=UTC

# A snapshot of the staged tree: sha256 and relative path, one line per file,
# in C order. Called at the points where something could have written into the
# tree, so that "which byte moved" is a diff rather than an argument.
snapshot() {  # $1 label -> $WORK/staged-$1.txt (and $DEBUG_DIR, if set)
  python3 - "$STAGE" "$WORK/staged-$1.txt" <<'PYSNAP'
import hashlib, os, sys
root, out = sys.argv[1], sys.argv[2]
rows = []
for d, dirs, files in os.walk(root):
    for n in files:
        p = os.path.join(d, n)
        rel = os.path.relpath(p, root)
        if os.path.islink(p):
            rows.append(("symlink:" + os.readlink(p), rel))
            continue
        h = hashlib.sha256()
        with open(p, "rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
        rows.append((h.hexdigest(), rel))
rows.sort(key=lambda r: r[1])
with open(out, "w", encoding="utf-8") as fh:
    for h, rel in rows:
        fh.write(f"{h}  {rel}\n")
PYSNAP
  [ -n "$DEBUG_DIR" ] && cp "$WORK/staged-$1.txt" "$DEBUG_DIR/staged-$1.txt"
  return 0
}

# A mirror that does not exist yet is created as a bare clone of its remote.
# On a maintainer's machine every mirror already exists and this is a no-op;
# in CI the runner starts empty and this is how the mirrors come to be, from
# the same public repositories, with no list of them kept anywhere else.
ensure_mirror() {  # $1 bare mirror path  $2 remote url
  [ -d "$1" ] && return 0
  echo "    creating mirror $1"
  if ! git clone --quiet --bare "$2" "$1"; then
    echo "BLOCKED: cannot create the mirror $1 from $2" >&2
    exit 1
  fi
}

# The scaffold's mirror is refreshed and compared with the remote before
# anything is staged. Staging the vault from a mirror that sits behind origin
# ships yesterday's scaffold under today's date.
echo "==> refreshing the scaffold mirror"
ensure_mirror "$SCAFFOLD_GIT" "$SCAFFOLD_REMOTE"
if ! git --git-dir "$SCAFFOLD_GIT" fetch --quiet --tags --force origin \
     "+refs/heads/main:refs/remotes/origin/main"; then
  echo "BLOCKED: cannot refresh the scaffold mirror from origin" >&2
  exit 1
fi
if [ -n "$SCAFFOLD_TAG" ]; then
  # The release workflow stages the tag it just created, not whatever main
  # holds by the time this runs: a second push landing during the build must
  # not leak into a zip published under the first push's version. The tag is
  # compared with the remote's copy the same way origin/main is below, so a
  # mirror carrying a tag the remote does not, or a different one, blocks.
  if ! scaffold_staged="$(git --git-dir "$SCAFFOLD_GIT" rev-parse -q --verify \
        "refs/tags/$SCAFFOLD_TAG^{commit}")"; then
    echo "BLOCKED: the scaffold mirror has no tag $SCAFFOLD_TAG after fetching origin" >&2
    exit 1
  fi
  # An annotated tag lists twice on the remote, the tag object and, with a
  # ^{} suffix, the commit it points at; the commit is what gets compared.
  scaffold_remote="$(git ls-remote --tags "$SCAFFOLD_REMOTE" \
    | awk -v peeled="refs/tags/$SCAFFOLD_TAG^{}" -v plain="refs/tags/$SCAFFOLD_TAG" \
        '$2==peeled{p=$1} $2==plain{q=$1} END{print (p!="")?p:q}')"
  if [ -z "$scaffold_remote" ]; then
    echo "BLOCKED: tag $SCAFFOLD_TAG is not on the scaffold remote" >&2
    exit 1
  fi
  if [ "$scaffold_staged" != "$scaffold_remote" ]; then
    echo "BLOCKED: tag $SCAFFOLD_TAG is $scaffold_staged in the mirror but $scaffold_remote on the remote" >&2
    exit 1
  fi
  scaffold_label="tag $SCAFFOLD_TAG"
else
  scaffold_staged="$(git --git-dir "$SCAFFOLD_GIT" rev-parse origin/main)"
  scaffold_remote="$(git ls-remote "$SCAFFOLD_REMOTE" refs/heads/main | cut -f1)"
  if [ "$scaffold_staged" != "$scaffold_remote" ]; then
    echo "BLOCKED: scaffold origin/main is $scaffold_staged but the remote reports $scaffold_remote" >&2
    exit 1
  fi
  scaffold_label="origin/main"
fi

echo "==> staging scaffold from git ($scaffold_label, tracked files only)"
git --git-dir "$SCAFFOLD_GIT" archive "$scaffold_staged" | tar -x -C "$STAGE"

# No plugin and no theme is staged (2.3.0). They were added here from their
# own repos and latest releases until 2.2.2; members now install them from
# Obsidian's community directory, which also keeps them up to date.

snapshot "01-after-staging"

fail=0

# ---------------------------------------------------------------------------
# 0a. THE TEST GATE
#
# No release while a guard has not been watched go red (GL-1005 rule 4).
# Every test-*.py suite in Scripts/ must pass, and must FAIL under
# --break-me, which flips one of its own assertions: a suite that cannot go
# red proves nothing. Until 2.2.2 this gate ran myPKA's run-red-tests.py on a
# merge with a pinned myPKA checkout; ICOR for Life is a content folder now
# and tests its own scripts.
#
# AGAINST A COPY, NEVER THE STAGED TREE. The suites import and run the tree's
# own scripts, and CPython writes a .pyc beside anything it imports; a .pyc
# carries the absolute path of its source, which ends in six random mktemp
# characters, so the zip would change on every build (what 1.23.0 died of).
# The copy is byte-identical, so the gate still proves these bytes refuse
# what they must refuse.
# ---------------------------------------------------------------------------
echo "==> test gate (every suite passes and every suite can go red)"
PROBE="$WORK/probe"
mkdir -p "$PROBE"
cp -a "$STAGE"/. "$PROBE"/
suites=0
for t in "$PROBE/06 AI Team/AI Team Knowledge/Scripts"/test-*.py; do
  [ -f "$t" ] || continue
  suites=$((suites + 1))
  name="$(basename "$t")"
  if ! out="$(PYTHONDONTWRITEBYTECODE=1 python3 -B "$t" 2>&1)"; then
    echo "BLOCKED tests: $name failed:"; printf '%s\n' "$out" | tail -15 | sed 's/^/                 /'; fail=1
  else
    echo "    $name: $(printf '%s\n' "$out" | tail -1)"
  fi
  if PYTHONDONTWRITEBYTECODE=1 python3 -B "$t" --break-me >/dev/null 2>&1; then
    echo "BLOCKED tests: $name passed under --break-me, so it cannot go red"; fail=1
  fi
done
if [ "$suites" -eq 0 ]; then
  echo "BLOCKED tests: no test-*.py suite in the staged Scripts/ (a gate with nothing to run is not a pass)"; fail=1
fi
rm -rf "$PROBE"

# The self-test hook for the assertion below: a gate that writes into the tree
# it is checking. Plant a file the way the red-test gate used to, and watch the
# next check refuse the build.
#   ICOR_ZIP_SELFTEST=stage-write bash build-release-zip.sh   # expect: BLOCKED
if [ "${ICOR_ZIP_SELFTEST:-}" = "stage-write" ]; then
  echo "    SELFTEST: writing into the staged tree after it was hashed; this build must fail"
  mkdir -p "$STAGE/06 AI Team/AI Team Knowledge/Scripts/__pycache__"
  printf 'planted by the stage-write self-test\n' \
    > "$STAGE/06 AI Team/AI Team Knowledge/Scripts/__pycache__/selftest.cpython-000.pyc"
fi

# NOTHING the gate did may have reached the bytes that ship. Hashing the tree
# either side is the general form of the rule: it does not know about .pyc, so
# it catches the next writer too, whatever it turns out to be.
snapshot "02-after-red-tests"
if ! cmp -s "$WORK/staged-01-after-staging.txt" "$WORK/staged-02-after-red-tests.txt"; then
  echo "BLOCKED: the gates changed the staged tree. A zip has to be a function of the commit,"
  echo "         and a gate that writes into the bytes it is checking makes it a function of"
  echo "         the run as well. Run the gate against a copy. What moved:"
  diff "$WORK/staged-01-after-staging.txt" "$WORK/staged-02-after-red-tests.txt" \
    | sed -n 's/^[<>] [0-9a-f]\{64\}  /         /p' | LC_ALL=C sort -u
  fail=1
fi

# ---------------------------------------------------------------------------
# 0. THE RESIDUE GATE
#
# This script is our build tooling. It names our local mirror layout, our
# output directory and our GitHub org. None of that is any use to a member,
# and all of it is a map of our internals. It stays in the repo, where it
# belongs, and it is dropped from the staged tree here.
#
# Removal on its own would be silent filtering: rename the file and the
# filter stops matching, and the build still goes green. So removal is done
# by EXACT PATH and blocks if the path is not there, and then an independent
# content scan that knows nothing about that path blocks if any of the
# fingerprints survive anywhere in the tree, under any name.
#
# The patterns below are deliberately narrow. `github.com/myICOR` is NOT one
# of them, because the README links to the plugin repos and that is
# legitimate. A gate that goes red on correct content gets switched
# off, and a switched-off gate is worse than no gate at all.
# ---------------------------------------------------------------------------
echo "==> residue gate (our build tooling out of the member download)"

# build-scaffold-manifest.py reads this array out of this file, so the
# manifest never describes a file the download does not carry. Keep it one
# quoted path per line.
declare -a RESIDUE_PATHS=(
  "06 AI Team/AI Team Knowledge/Scripts/build-release-zip.sh"
  # The red-test gate (release-gate-red-tests.sh) is no longer listed: since
  # 2.0.0 it lived in myPKA, and since 2.3.0 this build runs ICOR for Life's
  # own suites instead, so this repository does not track it. A listed path that is
  # not tracked blocks the build below and fails build-scaffold-manifest.py.
  # The release workflow is the same kind of thing one level up: it is how
  # this script runs on every push, it names the same internals, and a
  # workflow file inside a member's vault would do nothing but confuse.
  ".github/workflows/release.yml"
  # GitHub shows this file as the contribution rules (it overrides the org
  # default, which invites pull requests; this repository takes none). It is
  # about the repository, not the folder, and myPKA ships its own root
  # CONTRIBUTING.md into the same vault, so it lives under .github/.
  ".github/CONTRIBUTING.md"
  # Release tooling that came over from myPKA in 2.3.0, when this build
  # stopped needing a myPKA checkout. Ours now; no use to a member.
  "06 AI Team/AI Team Knowledge/Scripts/zip-staged-tree.sh"
  "06 AI Team/AI Team Knowledge/Scripts/check-version-bump.py"
)

# The self-test hook can only ever ADD a reason to fail. There is no value of
# ICOR_ZIP_SELFTEST that makes a failing gate pass, which is the property that
# makes it safe to leave in a release script. Run it before trusting a green:
#   ICOR_ZIP_SELFTEST=residue bash build-release-zip.sh   # expect: BLOCKED
#   ICOR_ZIP_SELFTEST=rename  bash build-release-zip.sh   # expect: BLOCKED
#   ICOR_ZIP_SELFTEST=plugin-workflow bash build-release-zip.sh   # expect: BLOCKED
#   ICOR_ZIP_SELFTEST=mypka   bash build-release-zip.sh   # expect: BLOCKED
# The fourth case, stage-write, is planted earlier, right after the red-test
# gate, because that is where the assertion it proves lives.
case "${ICOR_ZIP_SELFTEST:-}" in
  residue)
    echo "    SELFTEST: planting residue in the staged tree; this build must fail"
    printf 'staged from %s/.icor-git/scaffold.git\n' "\$HOME" \
      > "$STAGE/06 AI Team/selftest-planted-residue.md"
    ;;
  rename)
    echo "    SELFTEST: renaming the residue file; this build must fail"
    mv "$STAGE/06 AI Team/AI Team Knowledge/Scripts/build-release-zip.sh" \
       "$STAGE/06 AI Team/AI Team Knowledge/Scripts/build-release-zip.sh.bak"
    ;;
  plugin-workflow)
    # The 2026-09-07 shape: a plugin repo's own release workflow inside a
    # plugin folder. Three gates below must each refuse it: the .github
    # directory scan, the `runs-on:` pattern, and the no-bundle gate (no
    # plugin folder may be staged at all since 2.3.0).
    echo "    SELFTEST: planting a plugin repo's release workflow in a plugin folder; this build must fail"
    mkdir -p "$STAGE/.obsidian/plugins/icor-for-life-planner/.github/workflows"
    printf 'jobs:\n  release:\n    runs-on: ubuntu-latest\n' \
      > "$STAGE/.obsidian/plugins/icor-for-life-planner/.github/workflows/release.yml"
    ;;
  mypka)
    # The myPKA 7 shape: the team's entry file and an agent folder inside the
    # content folder. The no-myPKA gate must refuse both, by name and by
    # inventory.
    echo "    SELFTEST: planting myPKA files in the staged tree; this build must fail"
    printf '# AGENTS.md\n' > "$STAGE/AGENTS.md"
    mkdir -p "$STAGE/06 AI Team/Agents/Larry"
    printf '# Larry\n' > "$STAGE/06 AI Team/Agents/Larry/AGENT.md"
    ;;
esac

for rp in "${RESIDUE_PATHS[@]}"; do
  if [ ! -e "$STAGE/$rp" ]; then
    echo "BLOCKED residue: expected to remove '$rp' from the staged tree and it is not there."
    echo "                 It was renamed, moved, or dropped from the repo. Fix this list;"
    echo "                 do not assume the tree is clean because the removal found nothing."
    fail=1
    continue
  fi
  rm -rf "$STAGE/$rp"
  echo "    removed $rp"
done
# The workflow's folders are empty once it is gone, and an empty .github/
# inside a vault is an invitation to put something in it.
[ -d "$STAGE/.github" ] && find "$STAGE/.github" -depth -type d -empty -delete
# And no .github directory anywhere in the member download, whatever is in
# it: the scaffold's own is emptied and gone above, and no plugin folder is
# staged at all. The release
# workflow refuses `.github/` inside the finished zip as well; this is the
# same rule one step earlier, where the folder is named.
while IFS= read -r d; do
  [ -n "$d" ] || continue
  echo "BLOCKED residue: a .github directory survives at ${d#$STAGE/}"; fail=1
done < <(find "$STAGE" -type d -name ".github")

# Now the part that does not know the filename.
declare -a RESIDUE_PATTERNS=(
  "[.]icor-git"
  "HOME/Desktop"
  # Only a GitHub Actions workflow says this. A renamed workflow file, or
  # a copy of one anywhere in the tree, goes red here.
  "runs-on:"
  "YishenTu"
  "claudian"
)
for pat in "${RESIDUE_PATTERNS[@]}"; do
  if hits="$(grep -rIlE "$pat" "$STAGE" 2>/dev/null)"; then
    while IFS= read -r f; do
      [ -n "$f" ] || continue
      echo "BLOCKED residue: '$pat' survives in ${f#$STAGE/}"; fail=1
    done <<< "$hits"
  fi
  if hits="$(find "$STAGE" -iname "*${pat//[^a-zA-Z0-9-]/}*" 2>/dev/null)"; then
    while IFS= read -r f; do
      [ -n "$f" ] || continue
      echo "BLOCKED residue: a staged path is named after '$pat': ${f#$STAGE/}"; fail=1
    done <<< "$hits"
  fi
done
[ "$fail" -eq 0 ] && echo "    no residue in the staged tree"

# ---------------------------------------------------------------------------
# 0b. THE VERSION GATE
#
# The staged tree carries its own version folder, .icor-for-life/, and the
# Scaffold Check plugin in every member's vault trusts manifest.json to
# describe exactly the bytes that shipped. A manifest built before the last
# commit describes a tree nobody downloaded, and the plugin would then tell a
# member their untouched file "changed upstream". So the builder's --check
# runs against the STAGED tree, not the dev checkout: stale manifest, missing
# VERSION, or a removed file the changelog does not explain, and the build
# stops. It needs the git history for the removals, so it runs from the
# mirror with the staged tree as its work tree.
# ---------------------------------------------------------------------------
echo "==> version gate (.icor-for-life/manifest.json describes the staged tree)"
if [ ! -f "$STAGE/.icor-for-life/VERSION" ] || [ ! -f "$STAGE/.icor-for-life/manifest.json" ]; then
  echo "BLOCKED version: .icor-for-life/VERSION or manifest.json is missing from the staged tree"; fail=1
elif [ -n "$SCAFFOLD_TAG" ] && [ "$(tr -d '[:space:]' < "$STAGE/.icor-for-life/VERSION")" != "$SCAFFOLD_TAG" ]; then
  # A tag named after one version on a tree that calls itself another is
  # the moved-tag defect in a different coat, and --check below would not
  # see it: a tagged HEAD is trusted to be its own version.
  echo "BLOCKED version: staging tag $SCAFFOLD_TAG but the tree's VERSION reads $(tr -d '[:space:]' < "$STAGE/.icor-for-life/VERSION")"; fail=1
else
  # The builder needs `git ls-files` and the tag history, and a bare mirror
  # has neither an index nor a work tree. So: a throwaway clone of the mirror
  # checked out at the exact sha the tree was staged from. Same bytes as
  # $STAGE, plus the history the removal list is derived from.
  VCHECK="$(mktemp -d /tmp/icor-version-gate.XXXXXX)"
  if git clone -q "$SCAFFOLD_GIT" "$VCHECK" 2>/dev/null \
     && git -C "$VCHECK" checkout -q "$scaffold_staged" 2>/dev/null; then
    if ! python3 "$VCHECK/06 AI Team/AI Team Knowledge/Scripts/build-scaffold-manifest.py" --check; then
      echo "BLOCKED version: the staged manifest does not describe the staged tree (see FAIL lines above)"; fail=1
    fi
  else
    echo "BLOCKED version: cannot clone the scaffold mirror at $scaffold_staged to verify the manifest"; fail=1
  fi
  rm -rf "$VCHECK"
fi

echo "==> secret scan (the gate)"
# 1. Files that must never exist in a release
while IFS= read -r f; do
  echo "BLOCKED file: $f"; fail=1
done < <(find "$STAGE" \( -name ".env" -o -name "*.env" -o -name "workspace-mobile.json" \) -type f)

# 1b. THE FIRST-OPEN WORKSPACE, and why it is the one exception.
#
# A vault with no workspace opens on whatever Obsidian last felt like, which
# in practice was a third-party plugin's changelog: a member's first sight of
# the product was somebody else's release notes. So the scaffold ships ONE
# curated workspace whose only job is to open README.md.
#
# workspace.json is otherwise personal state and stays banned. It records
# every recently opened file and can carry absolute paths out of the author's
# machine, which is exactly what the blanket rule above existed to stop. The
# exception is therefore narrow AND checked, not narrow and trusted:
#   - exactly one path may exist, the vault-root .obsidian/workspace.json
#   - it may not contain an absolute home path
#   - lastOpenFiles may name README.md and nothing else
# A workspace that fails any of those is a leak, and the build stops.
while IFS= read -r f; do
  case "${f#$STAGE/}" in
    .obsidian/workspace.json) ;;
    *) echo "BLOCKED workspace at an unexpected path: ${f#$STAGE/}"; fail=1; continue ;;
  esac
  if ! python3 - "$f" <<'PYCHK'
import json, re, sys

# ONE STRUCTURAL RULE, not a list of remembered carriers.
#
# The first version of this check tested lastOpenFiles and a unix home path,
# and a review found both gaps immediately: a workspace can hold a personal
# note OPEN in a leaf while lastOpenFiles reads README.md, and a search pane
# keeps whatever the author last typed. A string test can only refuse the
# carrier somebody thought of, so this walks the parsed document instead and
# refuses anything that is not the one file we ship.
d = json.load(open(sys.argv[1]))
ALLOWED_FILE = 'README.md'
UNIX_HOME = re.compile(r'/(Users|home)/')
WIN_HOME = 'users'  # matched case-insensitively against a drive-letter path below
bad = []

def walk(node, path='$'):
    if isinstance(node, dict):
        for k, v in node.items():
            if k == 'file' and isinstance(v, str) and v != ALLOWED_FILE:
                bad.append(f'{path}.file names {v!r}')
            elif k == 'searchQuery' and isinstance(v, str) and v.strip():
                bad.append(f'{path}.searchQuery is not empty')
            elif k == 'lastOpenFiles' and isinstance(v, list):
                for item in v:
                    if item != ALLOWED_FILE:
                        bad.append(f'lastOpenFiles names {item!r}')
            else:
                walk(v, f'{path}.{k}')
    elif isinstance(node, list):
        for n, item in enumerate(node):
            walk(item, f'{path}[{n}]')
    elif isinstance(node, str):
        low = node.lower()
        drive = len(node) > 2 and node[1] == ':' and (chr(92) in node or '/' in node)
        if UNIX_HOME.search(node) or (drive and WIN_HOME in low):
            bad.append(f'{path} carries an absolute home path')

walk(d)
for b in bad:
    print(f'    {b}', file=sys.stderr)
sys.exit(1 if bad else 0)
PYCHK
  then
    echo "BLOCKED workspace carries state that is not the shipped README: ${f#$STAGE/}"; fail=1
  fi
done < <(find "$STAGE" -name "workspace.json" -type f)
# 2. data.json never ships. No plugin ships at all since 2.3.0, and a
#    plugin's settings file is the member's own.
while IFS= read -r f; do
  echo "BLOCKED data.json: $f"; fail=1
done < <(find "$STAGE" -name "data.json" -type f)
# 2b. Personal live data: planner items and dated daily notes never ship
while IFS= read -r f; do
  echo "BLOCKED personal data: $f"; fail=1
done < <(find "$STAGE/02 Planner" -type f ! -name "README.md" 2>/dev/null; \
         find "$STAGE/00 Daily Scratchpad" -type f -name "[0-9][0-9][0-9][0-9]-*.md" 2>/dev/null)
# 2c. A tracked .npmrc is the classic npm-token carrier. Clean today in every
#     repo, but `npm login` writes the token straight into it, so any auth
#     directive in a staged .npmrc blocks the zip.
while IFS= read -r f; do
  if grep -qiE "(_auth|_authToken|_password)[[:space:]]*=" "$f"; then
    echo "BLOCKED .npmrc with an auth directive: $f"; fail=1
  fi
done < <(find "$STAGE" -name ".npmrc" -type f)
# 3. Content patterns that look like live credentials
if grep -rInE "(pk_[0-9]+_[A-Z0-9]{20,}|xoxb-|BEGIN [A-Z ]*PRIVATE KEY|LEXOFFICE_API_KEY=|app_password|smtp_pass)" "$STAGE" 2>/dev/null \
     | grep -v "Scripts/run-red-tests.py"; then
  echo "BLOCKED: credential-like content found (see matches above)"; fail=1
fi

sha_of() { shasum -a 256 "$1" | cut -d' ' -f1; }

# ---------------------------------------------------------------------------
# 4. THE NO-BUNDLE GATE (2.3.0)
#
# The zip carries no Obsidian plugin and no theme. Members install the ICOR
# for Life plugins and the INKLINE theme from Obsidian's community directory,
# so a folder under .obsidian/plugins/ or .obsidian/themes/ in the staged
# tree is either a mistake that would ship code nobody released, or a
# leftover that would shadow the copy the member installs. And
# community-plugins.json enables nothing: enabling a plugin the zip does not
# hold is a "failed to load" notice on the member's first open.
#
# A check that cannot run goes RED: a missing or unreadable list blocks.
# ---------------------------------------------------------------------------
echo "==> no-bundle gate (no plugin or theme in the zip, nothing enabled)"
for d in ".obsidian/plugins" ".obsidian/themes"; do
  if [ -e "$STAGE/$d" ]; then
    while IFS= read -r f; do
      [ -n "$f" ] || continue
      echo "BLOCKED no-bundle: ${f#$STAGE/} is staged; plugins and themes come from Obsidian's community directory"; fail=1
    done < <(find "$STAGE/$d" -mindepth 1 -maxdepth 1 2>/dev/null)
  fi
done
CPJ="$STAGE/.obsidian/community-plugins.json"
if [ ! -f "$CPJ" ]; then
  echo "BLOCKED no-bundle: .obsidian/community-plugins.json is missing from the staged vault"; fail=1
elif ! ENABLED="$(python3 -c '
import json, sys
v = json.load(open(sys.argv[1], encoding="utf-8"))
if not isinstance(v, list):
    sys.exit("community-plugins.json is not a list")
for p in v:
    print(p)
' "$CPJ")"; then
  echo "BLOCKED no-bundle: .obsidian/community-plugins.json cannot be read as a list"; fail=1
elif [ -n "$ENABLED" ]; then
  while IFS= read -r p; do
    echo "BLOCKED no-bundle: community-plugins.json enables '$p', which the zip does not carry"; fail=1
  done <<< "$ENABLED"
else
  echo "    no plugin or theme staged, community-plugins.json enables nothing"
fi

# ---------------------------------------------------------------------------
# 4b. THE NO-myPKA GATE (2.3.0)
#
# ICOR for Life is a content folder. Agent teams come from myPKA 8, a separate
# download that keeps its own folder, so nothing of myPKA's may ride in this
# zip. Two locks, the same shape as the residue gate:
#   - by NAME: the paths myPKA owns (its entry files, its version folder, the
#     host folders, and the parts of 06 AI Team/ that are the team rather than
#     ICOR for Life's knowledge: agents, SOPs, skills, tasks, session logs,
#     AI sessions, expansions). A hit names what it found.
#   - by INVENTORY: every staged file must be listed in this release's
#     .icor-for-life/manifest.json `files`. A myPKA file under a name nobody
#     thought of is still not in the manifest, so it still blocks.
# ---------------------------------------------------------------------------
echo "==> no-myPKA gate (ICOR for Life ships its own files only)"
if ! MYPKA_HITS="$(python3 -c '
import json, os, sys
root = sys.argv[1]
ROOT_FILES = {"AGENTS.md", "AGENT.md", "ADAPTER-PROMPT.md", "CLAUDE.md", "GEMINI.md",
              ".mcp.json", "LICENSE", "LICENSE-MAP.md", "TRADEMARK.md", "CONTRIBUTING.md"}
PREFIXES = (".mypka/", ".claude/", ".codex/", ".gemini/", ".agents/", ".cursor/",
            "06 AI Team/Agents/", "06 AI Team/AI Sessions/", "06 AI Team/Expansions/",
            "06 AI Team/AI Team Knowledge/SOPs/", "06 AI Team/AI Team Knowledge/Skills/",
            "06 AI Team/AI Team Knowledge/Tasks/", "06 AI Team/AI Team Knowledge/Session Logs/")
staged = set()
for d, dirs, files in os.walk(root):
    for n in files:
        staged.add(os.path.relpath(os.path.join(d, n), root).replace(os.sep, "/"))
for rel in sorted(staged):
    low = rel.lower()
    if rel in ROOT_FILES or rel.startswith(PREFIXES) or ("/" not in rel and low.endswith("-mypka.md")):
        print("%s is a myPKA file" % rel)
man = json.load(open(os.path.join(root, ".icor-for-life/manifest.json"), encoding="utf-8"))
# .gitignore reaches a new download but is repo_only, never installed by the
# updater (placement row 9), so it is the one file outside `files`.
listed = set(man.get("files") or {}) | {".gitignore"}
for rel in sorted(staged - listed):
    print("%s is staged but not in .icor-for-life/manifest.json" % rel)
' "$STAGE")"; then
  echo "BLOCKED no-myPKA: the check could not run (manifest unreadable?)"; fail=1
elif [ -n "$MYPKA_HITS" ]; then
  while IFS= read -r line; do
    echo "BLOCKED no-myPKA: $line"; fail=1
  done <<< "$MYPKA_HITS"
else
  echo "    no myPKA file staged; every staged file is in the manifest"
fi

if [ "$fail" -ne 0 ]; then
  echo "RELEASE ABORTED: the staged tree is not clean." >&2
  exit 1
fi
echo "    scan clean"

NAME="ICOR-for-Life-Scaffold-$STAMP.zip"
# `zip -r` UPDATES an archive that already exists: new entries are added,
# changed ones replaced, and every entry the staged tree no longer has is
# kept. On 2026-09-04 a second build on one day merged into the morning's
# zip and shipped the plugin folder 1.7.0 had removed, while every gate
# above stayed green, because every gate above inspects the staged tree
# and none of them looks inside the zip. The archive is therefore removed
# first, so the zip is always a fresh copy of the tree the gates passed.
rm -f "$OUT_DIR/$NAME"
# REPRODUCIBLE. Two builds of the same tag must be the same bytes, or the release workflow could never tell "already
# published" from "different bytes under the same version". Two things make
# a zip differ for no reason: file times (git archive stamps the commit
# time, but the release downloads carry the moment they were fetched) and
# entry order (a directory walk is filesystem order). So every entry gets
# the staged commit's timestamp, the entries are written in one sorted
# order, and the zip carries no per-file extra attributes. The zip format
# keeps its times in local time, so the clock is pinned to UTC as well.
snapshot "03-before-zip"
echo "==> zipping -> $OUT_DIR/$NAME"
STAGE_EPOCH="$(git --git-dir "$SCAFFOLD_GIT" log -1 --format=%ct "$scaffold_staged")"
if ! sh "$ZIPPER" "$STAGE" "$OUT_DIR/$NAME" "$STAGE_EPOCH"; then
  echo "RELEASE ABORTED: the staged tree could not be archived reproducibly." >&2
  exit 1
fi
if [ -n "$DEBUG_DIR" ]; then
  # Per-entry length, method, compressed size, date, CRC-32 and name. A diff of
  # two of these says whether an entry moved in content, in size or only in
  # order, which is the one question a pair of zip hashes cannot answer.
  unzip -v "$OUT_DIR/$NAME" > "$DEBUG_DIR/zip-listing.txt"
  echo "    debug: zip entry listing -> $DEBUG_DIR/zip-listing.txt"
fi
echo "==> done: $OUT_DIR/$NAME ($(du -h "$OUT_DIR/$NAME" | cut -f1), sha256 $(sha_of "$OUT_DIR/$NAME"))"
