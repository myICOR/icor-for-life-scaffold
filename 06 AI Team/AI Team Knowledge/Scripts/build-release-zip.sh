#!/bin/bash
# Build a distribution zip of the ICOR for Life Scaffold that can NEVER
# contain personal data or API tokens, and can never contain an artifact
# whose version number disagrees with the bytes that number names.
#
# How safety is guaranteed:
#   1. The vault is never zipped directly. The scaffold content comes from
#      `git archive` of the scaffold repo: only tracked files ship, and
#      .env / workspace.json / our plugin folders (whose data.json holds
#      tokens) are gitignored, so they cannot be tracked.
#   2. The ICOR plugins and the INKLINE theme are added from their own
#      repos via `git archive` too, BY PATH: a plugin folder gets main.js,
#      manifest.json and styles.css, the theme gets manifest.json and
#      theme.css, and nothing else in those repos (sources, tests, their
#      own release workflows) can reach the zip. Those repos gitignore
#      data.json, and the shape is asserted again in the residue gate.
#   3. A secret scan runs over the staged tree and aborts on any hit.
#   4. THE ARTIFACT GATE: every bundled plugin and the theme is compared,
#      byte for byte, against the assets of its latest published GitHub
#      release. A version number is not evidence; the digest is.
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
#      tag with the same plugin releases gives the same bytes. The release
#      workflow relies on this: a re-run compares its zip with the asset
#      already published under that version instead of overwriting it.
#      The zip itself is written by zip-staged-tree.sh, which is a separate
#      file so that run-red-tests.py can build a fixture twice under two
#      locales and two clocks and assert one sha256.
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
# Why gate 4 exists. Three times a correct version number sat on top of the
# wrong bytes, and each time a person caught it, not a check:
#   - a plugin's manifest read 0.6.1 while its newest release was 0.4.2.
#   - the theme shipped tag 1.2.4 and a main that differed by 2,037 bytes
#     of CSS, both called 1.2.4, while it was live in the community
#     directory. Every version number agreed. Only the bytes disagreed.
#   - a test vault held a folder labelled 0.1.0 whose bytes were not 0.1.0.
# This script stages seven of the nine artifacts with `git archive main`
# (by path), so without gate 4 the next unbumped commit to any of them
# silently re-creates that defect inside the zip, where nobody is looking
# at git.
#
# Usage: bash build-release-zip.sh [output-dir]   (default: ~/Desktop)
#
# Environment (every one optional except MYPKA_TREE; the defaults are the
# local maintainer setup):
#   MYPKA_TREE            REQUIRED since the split (plan step 12): a myPKA
#                         checkout at the pinned tag. zip-staged-tree.sh and
#                         the red-test suite live there now. The gate runs on a
#                         mode A merge (the staged tree, this checkout over it);
#                         the zip holds the staged ICOR tree only.
#   ICOR_SCAFFOLD_TAG     stage this exact tag of the scaffold instead of
#                         origin/main. The release workflow sets it to the
#                         version it just tagged, so what ships is the tagged
#                         tree and nothing that landed on main after it. The
#                         tag must exist on the remote and its VERSION must
#                         equal the tag name.
#   ICOR_SCAFFOLD_GIT     the scaffold's bare mirror (default: the mirror
#                         beside the plugin mirrors). Created if missing.
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
MYPKA_TREE="${MYPKA_TREE:-}"
MYPKA_SCRIPTS="$MYPKA_TREE/06 AI Team/AI Team Knowledge/Scripts"
if [ -z "$MYPKA_TREE" ] || [ ! -f "$MYPKA_SCRIPTS/zip-staged-tree.sh" ] || [ ! -f "$MYPKA_SCRIPTS/release-gate-red-tests.sh" ]; then
  echo "RELEASE ABORTED: MYPKA_TREE must name a myPKA checkout at the pinned tag (zip-staged-tree.sh and the red-test gate live there since the split)" >&2
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

# The scaffold's own mirror gets the same treatment the five plugin mirrors
# get below. Staging the vault from a mirror that sits behind origin ships
# yesterday's scaffold under today's date, and nothing downstream would
# notice, because every artifact gate below inspects the PLUGINS.
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

# local repo name | github remote | destination in the vault | kind
declare -a SPECS=(
  "icor-for-life-planner|icor-for-life-planner|.obsidian/plugins/icor-for-life-planner|plugin"
  "icor-for-life-focus|icor-for-life-focus|.obsidian/plugins/icor-for-life-focus|plugin"
  "icor-for-life-connect|icor-for-life-connect|.obsidian/plugins/icor-for-life-connect|plugin"
  "icor-for-life-interface|icor-for-life-interface|.obsidian/plugins/icor-for-life-interface|plugin"
  "icor-for-life-scaffold-check|icor-for-life-scaffold-check|.obsidian/plugins/icor-for-life-scaffold-check|plugin"
  "icor-for-life-sqlite-viewer|icor-for-life-sqlite-viewer|.obsidian/plugins/icor-for-life-sqlite-viewer|plugin"
  "icor-for-life-inkline|icor-for-life-inkline|.obsidian/themes/ICOR for Life - INKLINE|theme"
)

echo "==> adding first-party plugins and theme from their repos"
# Fetch first. These local mirrors are a copy, and a copy silently behind the
# truth is the same defect this script exists to catch, one layer earlier: on
# 2026-08-30 all five sat behind origin/main while the zip staged from them.
# A mirror that cannot be refreshed blocks the build rather than shipping
# whatever it happens to hold.
# What a staged plugin or theme folder holds, and all it holds. A member's
# vault loads exactly these files; everything else in a plugin repo is the
# repo, not the artifact. On 2026-09-07 every plugin repo gained a
# `.github/workflows/release.yml` and a whole-repo archive carried six of
# them into the staged tree, where the residue scan's `runs-on:` pattern
# rightly refused them. Archiving by path means a new file in a plugin repo
# can never ride into the zip, and a path that is missing fails `git
# archive` and blocks, which is right: the artifact gate would refuse that
# folder anyway.
shipped_files() {  # $1 kind -> the space-separated file list
  case "$1" in
    theme) echo "manifest.json theme.css" ;;
    *)     echo "main.js manifest.json styles.css" ;;
  esac
}
declare -a STAGED_SHAPES=()   # "dest|files", asserted in the residue gate

for spec in "${SPECS[@]}"; do
  IFS='|' read -r repo remote dest kind <<< "$spec"
  ensure_mirror "$MIRRORS/$repo.git" "https://github.com/myICOR/$remote.git"
  if ! git --git-dir "$HOME/.icor-git/$repo.git" fetch --quiet --tags --force origin \
       "+refs/heads/main:refs/remotes/origin/main"; then
    echo "BLOCKED: cannot refresh $repo from origin; refusing to stage a stale mirror" >&2
    exit 1
  fi
  # Stage from origin/main, never the local branch: the local branch is a
  # convenience ref that can sit behind, and what ships must be what the
  # remote actually holds.
  staged_sha="$(git --git-dir "$HOME/.icor-git/$repo.git" rev-parse origin/main)"
  remote_sha="$(git ls-remote "https://github.com/myICOR/$remote.git" refs/heads/main | cut -f1)"
  if [ "$staged_sha" != "$remote_sha" ]; then
    echo "BLOCKED: $repo origin/main is $staged_sha but the remote reports $remote_sha" >&2
    exit 1
  fi
  mkdir -p "$STAGE/$dest"
  ship="$(shipped_files "$kind")"
  # shellcheck disable=SC2086
  if ! git --git-dir "$HOME/.icor-git/$repo.git" archive origin/main -- $ship | tar -x -C "$STAGE/$dest"; then
    echo "BLOCKED: $repo origin/main does not carry every shipped file ($ship); nothing else is staged from it" >&2
    exit 1
  fi
  STAGED_SHAPES+=("$dest|$ship")
done

# The chat and terminal plugins are full source repos that do NOT track their
# build output, and their dev worktrees may hold an in-flight build that never
# shipped. The zip therefore stages each entirely from its LATEST GitHub
# release: docs from the release tag, bundle from the release assets - the
# certified artifact by construction, independent of any dev state.
#
# The mirror fetch is a hard block, not a `|| true`. A soft fetch means a
# mirror that cannot reach origin stages whatever it happens to hold, under
# the name of a tag it may not have; that is the stale-mirror defect the
# specs above already refuse, and these artifacts are no different.
#
# remote | the docs staged from the release tag (the bundle comes from the assets)
declare -a RELEASE_SPECS=(
  "icor-for-life-chat|manifest.json LICENSE README.md THIRD-PARTY-NOTICES.md docs/provenance.md SECURITY.md"
  "icor-for-life-terminal|manifest.json LICENSE README.md THIRD-PARTY-NOTICES.md docs/handoff.md SECURITY.md"
  "icor-for-life-canvases|manifest.json LICENSE README.md THIRD-PARTY-NOTICES.md SECURITY.md docs/canvas-format.md docs/architecture.md"
  "icor-for-life-scratchpad|manifest.json LICENSE README.md THIRD-PARTY-NOTICES.md SECURITY.md docs/architecture.md"
)
declare -a RELEASE_REMOTES=()
for rspec in "${RELEASE_SPECS[@]}"; do
  IFS='|' read -r R_REMOTE R_DOCS <<< "$rspec"
  RELEASE_REMOTES+=("$R_REMOTE")
  echo "==> adding the $R_REMOTE plugin (from its latest GitHub release)"
  R_DEST="$STAGE/.obsidian/plugins/$R_REMOTE"
  mkdir -p "$R_DEST"
  R_TAG="$(gh release view --repo "myICOR/$R_REMOTE" --json tagName --jq .tagName)"
  if [ -z "$R_TAG" ]; then
    echo "BLOCKED: myICOR/$R_REMOTE has no published release to stage from" >&2
    exit 1
  fi
  ensure_mirror "$MIRRORS/$R_REMOTE.git" "https://github.com/myICOR/$R_REMOTE.git"
  if ! git --git-dir "$HOME/.icor-git/$R_REMOTE.git" fetch --quiet --tags --force origin \
       "+refs/heads/main:refs/remotes/origin/main"; then
    echo "BLOCKED: cannot refresh the $R_REMOTE mirror from origin" >&2
    exit 1
  fi
  # The tag has to exist in the mirror after that fetch. Without this check a
  # missing tag reaches `git archive` as an unresolved rev, and the failure
  # reads like a build error rather than what it is: staging a release the
  # mirror has never seen.
  if ! git --git-dir "$HOME/.icor-git/$R_REMOTE.git" rev-parse -q --verify "refs/tags/$R_TAG" >/dev/null; then
    echo "BLOCKED: the $R_REMOTE mirror has no tag $R_TAG after fetching origin" >&2
    exit 1
  fi
  # shellcheck disable=SC2086
  git --git-dir "$HOME/.icor-git/$R_REMOTE.git" archive "$R_TAG" -- $R_DOCS \
    | tar -x -C "$R_DEST"
  gh release download "$R_TAG" --repo "myICOR/$R_REMOTE" \
    --pattern main.js --pattern styles.css --dir "$R_DEST" --clobber
done

snapshot "01-after-staging"

fail=0

# ---------------------------------------------------------------------------
# 0a. THE RED-TEST GATE
#
# No release while a guard has not been watched go red (GL-1005 rule 4).
#
# Until 2026-09-14 run-red-tests.py was run "on demand", which meant by
# nobody: two of its gates sat red for three days because check-bases.py
# could not import PyYAML, and the suite kept being described as green
# (tsk-2026-09-11-005). A runner nobody runs is a document. This is the one
# place that has to run it.
#
# It runs against $STAGE, the bytes that will ship, not the dev checkout.
# A staged tree has no .git, so the suite's manifest guards report SKIP with
# their reason rather than dying, and a skip prints as itself.
#
# The gate body lives in its own file so that run-red-tests.py can test the
# gate: this script needs a git mirror, the gh CLI and the network, and a
# red test cannot call it.
# ---------------------------------------------------------------------------
echo "==> red-test gate (no release while a guard has not been watched go red)"
# AGAINST A COPY, NEVER THE STAGED TREE. The suite runs the tree's own scripts,
# and one of them is imported rather than spawned, so CPython writes a .pyc
# beside it; a .pyc carries the absolute path of its source, and the staged
# tree's path ends in six random mktemp characters. Three entries of the zip
# changed on every build, which is what the release workflow's reproducibility
# comparison went red on for 1.23.0. The copy is byte-identical, so the gate
# still proves what it always proved: these bytes refuse what they must refuse.
PROBE="$WORK/probe"
mkdir -p "$PROBE"
cp -a "$STAGE"/. "$PROBE"/
# Mode A merge: the pinned myPKA checkout over the copy, so the suite and the
# guards it tests are there. Never over $STAGE.
( cd "$MYPKA_TREE" && tar -c --exclude=.git . ) | tar -x -C "$PROBE"
if ! PYTHONDONTWRITEBYTECODE=1 sh "$PROBE/06 AI Team/AI Team Knowledge/Scripts/release-gate-red-tests.sh" "$PROBE"; then
  echo "BLOCKED red-tests: the staged tree carries a guard that did not refuse what it must refuse"; fail=1
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
# of them, because the bundled plugin READMEs link to their own repos and
# that is legitimate. A gate that goes red on correct content gets switched
# off, and a switched-off gate is worse than no gate at all.
# ---------------------------------------------------------------------------
echo "==> residue gate (our build tooling out of the member download)"

# build-scaffold-manifest.py reads this array out of this file, so the
# manifest never describes a file the download does not carry. Keep it one
# quoted path per line.
declare -a RESIDUE_PATHS=(
  "06 AI Team/AI Team Knowledge/Scripts/build-release-zip.sh"
  # The red-test gate (release-gate-red-tests.sh) is no longer listed: since
  # 2.0.0 it lives in myPKA (repo-only there) and this build calls it from
  # MYPKA_TREE, so this repository does not track it. A listed path that is
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
)

# The self-test hook can only ever ADD a reason to fail. There is no value of
# ICOR_ZIP_SELFTEST that makes a failing gate pass, which is the property that
# makes it safe to leave in a release script. Run it before trusting a green:
#   ICOR_ZIP_SELFTEST=residue bash build-release-zip.sh   # expect: BLOCKED
#   ICOR_ZIP_SELFTEST=rename  bash build-release-zip.sh   # expect: BLOCKED
#   ICOR_ZIP_SELFTEST=plugin-workflow bash build-release-zip.sh   # expect: BLOCKED
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
    # staged plugin folder. Three gates below must each refuse it: the
    # folder shape, the .github directory scan, and the `runs-on:` pattern.
    echo "    SELFTEST: planting a plugin repo's release workflow in a staged plugin folder; this build must fail"
    mkdir -p "$STAGE/.obsidian/plugins/icor-for-life-planner/.github/workflows"
    printf 'jobs:\n  release:\n    runs-on: ubuntu-latest\n' \
      > "$STAGE/.obsidian/plugins/icor-for-life-planner/.github/workflows/release.yml"
    ;;
esac

# The first-party plugin and theme folders were staged by path above. Here
# each one is asserted to hold exactly those files, so a loosened archive
# line, or anything else that lands a file in one of them, goes red on its
# own, before the content scan below gets its turn.
for shape in "${STAGED_SHAPES[@]}"; do
  IFS='|' read -r dest ship <<< "$shape"
  # shellcheck disable=SC2086
  want="$(printf '%s\n' $ship | LC_ALL=C sort)"
  have="$(cd "$STAGE/$dest" && find . -type f | sed 's|^\./||' | LC_ALL=C sort)"
  if [ "$have" != "$want" ]; then
    echo "BLOCKED residue: $dest must hold exactly [$ship] and holds:"
    while IFS= read -r f; do echo "                 $f"; done <<< "$have"
    fail=1
  fi
done

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
# it: the scaffold's own is emptied and gone above, and a plugin's never
# reaches the stage now that plugins are archived by path. The release
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
# 2. data.json never ships. Every plugin in the vault is first-party now and
#    keeps its own settings out of the vault's tracked history (the same rule
#    every other ICOR plugin already followed); there is no bundled
#    community plugin left to carve an exception for.
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
     | grep -v "Scripts/run-red-tests.py" \
     | grep -v "plugins/icor-for-life-chat/main.js"; then
  echo "BLOCKED: credential-like content found (see matches above)"; fail=1
fi

# ---------------------------------------------------------------------------
# 4. THE ARTIFACT GATE
#
# For every bundled artifact: the staged manifest version must equal the tag
# of that repo's latest published release, and every required asset must be
# byte-identical to the asset published under that tag.
#
# This is the clause that catches the theme shape. Comparing version
# NUMBERS passes when a repo re-uses a number over changed bytes; only the
# digest comparison fails. Note that four of these are staged from `git
# archive main`, so this compares main's bytes against what the world can
# actually download.
#
# A check that cannot run must go RED, never green. Missing digest, missing
# asset, missing release: all block.
# ---------------------------------------------------------------------------
echo "==> artifact gate (staged bytes vs published release assets)"

sha_of() { shasum -a 256 "$1" | cut -d' ' -f1; }

verify_artifact() {  # $1 label  $2 remote  $3 staged dir  $4 space-separated asset list
  local label="$1" remote="$2" dir="$3" assets="$4"
  local rel tag ver a want got

  if ! rel="$(gh api "repos/myICOR/$remote/releases/latest" 2>/dev/null)"; then
    echo "BLOCKED $label: no published release found on myICOR/$remote"; fail=1; return
  fi
  tag="$(printf '%s' "$rel" | python3 -c 'import sys,json;print(json.load(sys.stdin).get("tag_name",""))')"
  if [ -z "$tag" ]; then
    echo "BLOCKED $label: latest release has no tag name"; fail=1; return
  fi

  if [ ! -f "$dir/manifest.json" ]; then
    echo "BLOCKED $label: no manifest.json staged at $dir"; fail=1; return
  fi
  ver="$(python3 -c "import json;print(json.load(open('$dir/manifest.json')).get('version',''))")"
  if [ "$ver" != "$tag" ]; then
    echo "BLOCKED $label: staged manifest version ($ver) != latest release tag ($tag)"
    fail=1
  fi

  for a in $assets; do
    if [ ! -s "$dir/$a" ]; then
      echo "BLOCKED $label: staged asset $a is missing or empty"; fail=1; continue
    fi
    want="$(printf '%s' "$rel" | python3 -c "
import sys,json
d=json.load(sys.stdin)
for x in d.get('assets',[]):
    if x['name']=='$a':
        print((x.get('digest') or '').replace('sha256:',''))
        break
")"
    if [ -z "$want" ]; then
      echo "BLOCKED $label: release $tag publishes no digest for $a (cannot verify, so this is a failure, not a pass)"
      fail=1; continue
    fi
    got="$(sha_of "$dir/$a")"
    if [ "$want" != "$got" ]; then
      echo "BLOCKED $label: $a staged ${got:0:12} != release $tag ${want:0:12} - the zip would ship different bytes than the world downloads"
      fail=1
    else
      echo "    $label $a ${got:0:12} matches release $tag"
    fi
  done
}

for spec in "${SPECS[@]}"; do
  IFS='|' read -r _repo remote dest kind <<< "$spec"
  if [ "$kind" = "theme" ]; then
    verify_artifact "$remote" "$remote" "$STAGE/$dest" "manifest.json theme.css"
  else
    verify_artifact "$remote" "$remote" "$STAGE/$dest" "main.js manifest.json styles.css"
  fi
done
for R_REMOTE in "${RELEASE_REMOTES[@]}"; do
  verify_artifact "$R_REMOTE" "$R_REMOTE" "$STAGE/.obsidian/plugins/$R_REMOTE" "main.js manifest.json styles.css"
done

# 5. The enabled-plugin list and the staged plugin folders must agree.
#    Enabling a plugin the zip does not ship, or shipping one the vault does
#    not enable, is a silent broken install for whoever unzips this.
echo "==> enabled-plugin coherence"
CPJ="$STAGE/.obsidian/community-plugins.json"
if [ ! -f "$CPJ" ]; then
  echo "BLOCKED: .obsidian/community-plugins.json is missing from the staged vault"; fail=1
else
  COHERENCE="$(python3 - "$CPJ" "$STAGE/.obsidian/plugins" <<'PY'
import json, os, sys
enabled = set(json.load(open(sys.argv[1])))
present = {d for d in os.listdir(sys.argv[2])
           if os.path.isfile(os.path.join(sys.argv[2], d, "manifest.json"))}
# Every plugin in the vault is first-party now; there is no third-party
# plugin left to carve out of the coherence rule.
ours = {"icor-for-life-planner", "icor-for-life-focus",
        "icor-for-life-connect", "icor-for-life-chat", "icor-for-life-interface",
        "icor-for-life-scaffold-check", "icor-for-life-sqlite-viewer",
        "icor-for-life-terminal", "icor-for-life-outliner",
        "icor-for-life-pdf-annotation", "icor-for-life-canvases",
        "icor-for-life-scratchpad"}
for p in sorted((enabled & ours) - present):
    print(f"community-plugins.json enables {p!r} but the zip stages no such plugin folder")
for p in sorted((present & ours) - enabled):
    print(f"the zip stages {p!r} but community-plugins.json does not enable it")

# THE INVENTORY ASSERTION. The two rules above are set differences over the
# first-party set, so a plugin folder under a name that is not in `ours` is
# invisible to them: a folder left behind by a rename ships, enabled or not,
# and every check above stays green. This one names the complete expected
# tree instead, so anything extra or missing is a failure by construction
# rather than by remembering to add it to a list.
expected = ours
for p in sorted(present - expected):
    print(f"the zip stages an unexpected plugin folder {p!r}")
for p in sorted(expected - present):
    print(f"the zip is missing the plugin folder {p!r}")
PY
)"
  if [ -n "$COHERENCE" ]; then
    while IFS= read -r line; do
      echo "BLOCKED: $line"; fail=1
    done <<< "$COHERENCE"
  else
    echo "    enabled plugins and staged plugin folders agree"
  fi
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
# REPRODUCIBLE. Two builds of the same tag with the same plugin releases must
# be the same bytes, or the release workflow could never tell "already
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
if ! sh "$MYPKA_SCRIPTS/zip-staged-tree.sh" "$STAGE" "$OUT_DIR/$NAME" "$STAGE_EPOCH"; then
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
