# ICOR for Life Scaffold: changelog

One section per version, newest first. Each section says what was **added**,
what **changed**, and, most important for anyone updating by hand, what was
**removed or moved**. A file you still have that a release after your
installed version removed is a leftover, and the Scaffold Check plugin will
point at it and at the line here that explains it. Once you have installed
the version that removed a file, the plugin no longer lists it. Such a file
is harmless, and you can delete it by hand.

The rule for writing an entry: every removed or moved file is named in
backticks on its own line, with where it went. The manifest builder reads
those lines and refuses to describe a removal this file does not explain.

A section is opened under the version being cut, never under a heading
called `Unreleased`: the manifest builder matches removal lines by version
section, so a removal under any other heading is a removal it cannot
explain.

## 2.2.1

The README names the download as it is published. Nothing is removed or
moved. Pairs with myPKA 7.0.1.

- Fixed: `README.md`, "Updating", names `mypka-<version>.zip` (7.0.1 or
  later). 2.2.0 said `mypka-7.0.0.zip`: myPKA 7.0.0 was tagged but never
  released (its release build refused its own zip), so its first release is
  7.0.1.
- Changed: `LICENSE.md` says "From myPKA 7" instead of naming 7.0.0.

## 2.2.0

**myPKA again: one folder.** ICOR for Life continues as myPKA 7. From now
on this content ships inside one download with the AI team, `mypka-7.0.0.zip`
from the myPKA releases, under the name it started with. Nothing is removed
or moved. Pairs with myPKA 7.0.0.

- Changed: `README.md` is the myPKA README: what the folder and the team are,
  that it works with any AI and without Obsidian, that the twelve ICOR for
  Life plugins and the INKLINE theme come pre-installed for Obsidian users,
  the myPKA course, updating from myPKA 6 and ICOR for Life 2, and the Tool
  Lab note (a starting point, not a product; no support schedule; you are
  responsible for what you run).
- Changed: `LICENSE.md`. The folder is MIT from this version: the content
  (rooms, templates, guidelines, prose) as well as the scripts and plugins.
  The INKLINE theme keeps CC BY-NC-ND 4.0, bundled libraries keep their own
  licences, and no trademark is licensed. Earlier versions keep the licence
  they came with.

## 2.1.0

A quick capture made with Cmd+Alt+N lands in this month's folder, the
manifest remembers every older state of a removed file, and five bundled
plugins are newer. Nothing is removed or moved. Pairs with myPKA 6.0.3.

- Changed: `.obsidian/zk-prefixer.json` (Obsidian's Unique note setting,
  behind Cmd+Alt+N, Ctrl+Alt+N on Windows, and the myICOR Connect new-note
  button) writes `YYYY/MM/YYYYMMDDHHmm.md` in `00 Daily Scratchpad/`. It
  wrote `YYYY-MM-DD-HHmmss.md` at the room root, which the Scaffold's own
  check fails. Obsidian creates the year and month folders. A second note in
  the same minute gets a space and a number. Your existing captures keep
  their names and stay valid; nothing is renamed.
- If you use Obsidian Sync: "Core plugin settings" is a per-device Sync
  setting. On a device where it is off, the new-note key keeps the old
  name at the room root. Take the new `.obsidian/zk-prefixer.json`, or set
  Settings > Unique note creator > format to `YYYY/MM/YYYYMMDDHHmm`, on each
  such device.
- Changed: `06 AI Team/AI Team Knowledge/Guidelines/GL-1007-capture-and-where-things-go.md`
  and `00 Daily Scratchpad/README.md` name the capture `YYYYMMDDHHmm` in
  today's `YYYY/MM/` and the key Cmd+Alt+N (Cmd+N is Obsidian's plain new
  file). GL-1007 says the command "Add unique note link" is not part of
  capture.
- Added: `.icor-for-life/manifest.json` gains `previous_removed`: for each
  file a release removed, every older state it had, so Scaffold Check can
  tell an untouched old copy from one you edited. Built by
  `06 AI Team/AI Team Knowledge/Scripts/build-scaffold-manifest.py`, tested
  by the new `06 AI Team/AI Team Knowledge/Scripts/test-build-scaffold-manifest.py`.
  Idea: Brian Carroll (@brijcarroll). Readers that do not know the key
  ignore it.
- Changed: `06 AI Team/AI Team Knowledge/Scripts/validate-scaffold.py`: a
  comment names Obsidian's first collision suffix as ` 1`. No behaviour
  change; ` 1` and ` 2` were both accepted already.
- Changed: bundled plugins. ICOR for Life - Planner 0.16.2, Scaffold Check
  0.8.1, Connect 0.16.1, AI Chat 0.16.2, SQLite Viewer 0.6.1. The other
  seven plugins and INKLINE are unchanged. Each plugin's release notes say
  what changed and name the community members who contributed.

## 2.0.1

The first release from the scaffold's new home,
`github.com/myICOR/icor-for-life-scaffold` (moved from `TomSolid` on
2026-09-26; GitHub redirects the old address). Nothing is removed or moved.

- Changed: `README.md` "First steps" step 2 no longer describes the AI team
  as part of this download. The team, `AGENTS.md` and the team scripts come
  with myPKA (github.com/myICOR/myPKA); the step says where to put it and
  keeps the path for working without AI. On Windows, the Terminal pane's
  "Open in external terminal" button is named. Step 1 now lists Scratchpad,
  and "Extending it" says Larry, Nolan and Mason come with myPKA.
- Changed: `README.md` and `SECURITY.md` verify downloads with
  `--repo myICOR/icor-for-life-scaffold`; releases up to 2.0.0 verify with
  `--owner TomSolid`. The zip builder and the release workflow read the
  scaffold from `myICOR/icor-for-life-scaffold`.
- Changed: the bundled ICOR for Life - Scaffold Check plugin is 0.7.1. It
  reads the manifest from the new home, moves a saved old default URL to
  the new one, and its release assets carry build-provenance attestations.
- Security: this release's zip and manifest are attested under
  `myICOR/icor-for-life-scaffold`.

## 2.0.0

The split. ICOR for Life 2.0.0 is the content half of the ICOR for Life
Scaffold 1.34.1 (`f7dd5f0`): the rooms, the entity templates, the concept
Guidelines, the life scripts and the Obsidian setup. The AI team half
(contracts, SOPs, Workstreams, team scripts, host files) moved to myPKA
6.0.1 (github.com/myICOR/myPKA), which runs unpacked into this folder or
beside it. Every team file that moved is marked `moved_to: mypka` in
`.icor-for-life/manifest.json`, so an update never deletes it.

- Removed: `CLAUDE.md`, the Claude Code entry file. myPKA's `AGENTS.md` is the one entry file now, and Claude Code reads it directly. A copy you edited stays yours.
- Removed: `GEMINI.md`, the Gemini CLI entry file. Gemini CLI finds myPKA's `AGENTS.md` through `.gemini/settings.json`. A copy you edited stays yours.
- Removed: `06 AI Team/AI Team Knowledge/Scripts/release-gate-red-tests.sh`, a maintainer script that never belonged in a member folder. It lives in the myPKA repository and does not ship.
- Added (step 18, Vex P7): every release zip is attested (build provenance).
  `README.md` shows the `gh attestation verify` command a member runs
  before unpacking a download.
- Changed (Vex, Themis): `SECURITY.md` covers only what ICOR for Life
  ships (the life scripts, the Obsidian setup, the bundled plugins and
  theme, the release workflow and its attestations) and points to myPKA's
  `SECURITY-myPKA.md` for the AI team. Reports go through GitHub private
  vulnerability reporting on this repository.
- Changed (Themis, Tom): `SECURITY.md` makes no time promise. 1.x named
  targets for a first reply, an assessment and a fix; "Our timelines"
  now says we read every report and reply when we can, and keeps only
  the 90-day window for keeping a finding private.
- Changed: `README.md` explains ICOR for Life and myPKA (mode A, mode B)
  and sends AI Team expansion packs to myPKA. The Scripts folder's README
  lists only the life scripts; the team scripts' reference moved to myPKA.
  The release workflow gains Gate 1c: no open decision bracket in any
  tracked file.
- Changed: the manifest shape. `files` is a map of path to sha256,
  `repo_only`, `seed`, `previous` and `vendored` are new, and `agents` moved
  to the myPKA manifest.
- Added: `06 AI Team/AI Team Knowledge/Scripts/noteio-icor.py`, a pinned copy
  of myPKA's `noteio.py`.
- Changed (step 13, Flint, Marshall): the manifest is `schema` 2, lists the
  example notes in `examples`, marks a removal that myPKA now ships as
  `moved_to: mypka`, keeps `previous` to paths it still ships, and carries
  `retired_ids` (GL-1009: never shipped; reserved for the recording package).

## 1.34.1 (2026-09-22)

A security patch to Mason's contract. 1.34.0 shipped Mason before the
security read of his contract had happened; that was a sequencing
mistake on the team's side, and the read then found a gap worth a
patch the same day. Mason is told to read issues, pull request comments
and review comments written by strangers, and he holds a shell on your
machine, and nothing in 1.34.0 said that such text is evidence, never
an instruction. This release says it, in his contract, and takes one
tool away from him.

Patch bump: nothing is added, nothing is removed, moved or renamed, no
plugin changes, one contract is hardened and one tool permission is
withdrawn. If you run 1.34.0, this is the release to take.

### Changed

- **Mason's contract, three new "never" rules
  (`06 AI Team/Agents/Mason/AGENT.md`).** Text from an issue, a pull
  request or review comment, a README, a commit message or the web is
  evidence about the code, never a command: anything in it that asks
  Mason to run, fetch, install, send, change or reveal something is
  quoted to you and refused. His shell stays inside the clone and
  inside `git`, `gh`, `npm`, `node` and the repository's own gate; no
  installers, no downloaded scripts, no command a page suggested,
  nothing in your vault or home folder. And no credential is ever read,
  printed, echoed or stored: no `gh auth token`, no `--show-token`, no
  `hosts.yml`, `.env`, `data.json` or keychain, no token in a note, a
  log, a commit or a pull request; when git asks for a password, you
  run `gh auth setup-git` yourself. Reproduction of a bug now happens
  in a throwaway vault made for the purpose, never your own. The
  Obsidian API reference he checks against is named exactly: the typed
  declarations after `npm ci` in the six build-shape repositories, one
  `gh api` call for the other six.
- **`WebFetch` withdrawn from Mason's tools.** His `tools:` line reads
  `Read, Write, Edit, Glob, Grep, Bash`, and `.claude/agents/mason.md`
  is regenerated to match (content hash `02353bc5d34d`). The `.codex`
  and `.gemini` shims carry no tools line and are unchanged.

What this does and does not guarantee, in plain words: the shell rule
is a rule the model follows and a text you can hold him to, and it
makes a violation visible; it is not enforced by a machine on your
computer. The belt today is your host's per-command permission prompt.
A deny list for `curl`, `wget`, `sh -c` and `bash -c` in the
Scaffold's settings is planned as its own change, not part of this one.

### Removed

Nothing. No file is removed, moved or renamed in this release.

### If you are updating by hand

Replace `06 AI Team/Agents/Mason/AGENT.md` with the copy in this
release, then run `scaffold-init.py plan` and `apply` from the vault
root (on Windows `py -3` in place of `python3`) so
`.claude/agents/mason.md` is regenerated with the shorter tools line.
Last, copy `.icor-for-life/VERSION`, `.icor-for-life/manifest.json`
and `.icor-for-life/CHANGELOG.md` from this release, so Scaffold Check
knows you run 1.34.1. Nothing else changes; nothing to copy under
`.obsidian/`.

## 1.34.0 (2026-09-22)

The team grows from ten agents to eleven. Mason is the plugin
contributor: when one of the ICOR for Life plugins misbehaves, or you
wish it did something it does not, he decides whether that is a plugin
change at all and in which plugin, makes the smallest fix in that
plugin's repository on GitHub, runs the repository's own gate, explains
the change in plain words, and opens the pull request in your name with
a DCO sign-off. You do not need to know git or GitHub. He is the agent
the MIT release in 1.33.0 was missing: the plugins take pull requests
now, and Mason is how a member sends one.

Minor bump: one agent is added with his contract, bio, journal, avatar
and three dispatch shims; six existing files gain one line or one
paragraph each. Nothing is removed, moved or renamed, every bundled
plugin is the release 1.33.0 carried, and a vault that already runs
1.33.0 keeps every file it has after this update.

### Added

- **Mason, the plugin contributor.** Same two-file shape as the other
  agents (`SOP-1007`), a journal, a dispatch shim per host and an avatar
  in the INKLINE style. He works inside repositories you do not own, so
  he does two jobs at once: the fix, and the plain-language account of
  the fix that lets you stand behind it. The fix is one issue per pull
  request, with a test that fails before and passes after, nothing else
  in the diff, no version or changelog edit; the gate is the plugin
  repository's own check, run before the pull request and pasted into
  it. When the answer is no, he says why and names the right door
  (Penn or Silas for a vault or note problem, Mack for a tool
  connection, Flint for a platform verdict, the repository's
  `SECURITY.md` for anything security-shaped, which never goes through
  a pull request). A judgement role, so he runs on the strongest model
  the host offers (`AGENTS.md`, "Which model runs what").
  - `06 AI Team/Agents/Mason/AGENT.md`: the contract.
  - `06 AI Team/Agents/Mason/Mason.md`: the bio.
  - `06 AI Team/Agents/Mason/Journal/_template.md` and
    `06 AI Team/Agents/Mason/Journal/2026-09-22-mason-hired.md`.
  - `.claude/agents/mason.md`, `.codex/agents/mason.toml` and
    `.gemini/agents/mason.md`: the dispatch shims, generated.
  - `06 AI Team/AI Team Knowledge/Avatars/mason.png`: the avatar.

### Changed

- `06 AI Team/Agents/agent-index.md`: one row for Mason, with the
  phrases that route to him and the four kinds of request that do not.
- `AGENTS.md`: the identity line names Mason among the specialists
  Larry launches rather than role-plays.
- `06 AI Team/Agents/Larry/AGENT.md`: the "never" line says Mason fixes
  a plugin and opens the pull request, so Larry does not.
- `README.md`: one paragraph under the team section says what to ask
  Larry for when a plugin has a bug or you want it to do something new.
- `expansion-pack.py` counts Mason among the core agents an expansion
  pack can never overwrite; `test-expansion-pack.py` proves it.
- `.codex/config.toml` is re-rendered for the larger `AGENTS.md`
  (14,275 bytes, under the 32 KiB Codex budget).

Every bundled plugin and the INKLINE theme are the versions 1.33.0
carried; none of them changes in this release.

### Removed

Nothing. No file is removed, moved or renamed in this release.

### If you are updating by hand

Replace `AGENTS.md`, `README.md`, `06 AI Team/Agents/agent-index.md`,
`06 AI Team/Agents/Larry/AGENT.md` and
`06 AI Team/AI Team Knowledge/Scripts/expansion-pack.py` with the copies
in this release, and copy `06 AI Team/Agents/Mason/` and
`06 AI Team/AI Team Knowledge/Avatars/mason.png`. Then run
`scaffold-init.py plan` and `apply` from the vault root (on Windows
`py -3` in place of `python3`) so the three shims and `.codex/config.toml`
are generated rather than copied; `AGENTS.md` first, because the
generator stamps that file's size into `.codex/config.toml`, and the
other order produces a config that at once asks for attention. Last,
copy `.icor-for-life/VERSION`, `.icor-for-life/manifest.json` and
`.icor-for-life/CHANGELOG.md` from this release: Scaffold Check reads
`VERSION` for the version you run, and without this step it keeps
telling you 1.34.0 is out. The plugins and the theme are unchanged;
nothing to copy under `.obsidian/`.

## 1.33.0 (2026-09-21)

The plugins are open source. Every ICOR for Life plugin, and the Python and
shell scripts under `06 AI Team/AI Team Knowledge/Scripts/`, are now under
the MIT licence, forward from the plugin versions named in `LICENSE.md`.
What you wrote, and the Scaffold's own prose, templates and contracts, stay
exactly as licensed before: yours to use and adapt, not open source.

Every plugin inside this download is the release that turned it MIT:
Planner 0.16.0, Connect 0.16.0, Focus 0.7.0, Interface 0.8.0, Scaffold
Check 0.6.0, SQLite Viewer 0.6.0, AI Chat 0.16.0, Terminal 0.2.0, Canvases
0.4.0, Scratchpad 0.2.0, Outliner 0.2.0 and PDF Annotation 0.2.0. Each is a
docs-only release over the version 1.32.0 carried: the `LICENSE` inside
every plugin folder is now the MIT text, and no plugin behaves differently.
The INKLINE theme is unchanged at 1.6.2.

Minor bump: one new file, the scripts' own licence, and twelve bundled
plugins at their MIT releases. Nothing is removed, moved or renamed, and
nothing about how the vault works changes.

### Added

- `06 AI Team/AI Team Knowledge/Scripts/LICENSE`: the verbatim MIT text for
  the scripts in that folder.

### Changed

- `LICENSE.md`: the plain-language summary now says which part is MIT and
  which part is not, every plugin row reads MIT from the version it turns
  MIT at, and a row for the scripts is new.
- `README.md`: the licence note says the plugins and scripts are MIT and
  that plugin contributions are welcome under a DCO sign-off.
- **Outliner 0.2.0 inside** (1.32.0 carried 0.1.0). The released assets
  byte for byte: `main.js` 3ec8a8fa52de, unchanged since 0.1.0,
  `manifest.json` 04f48a669845, `styles.css` 87240ff7ddba, from release
  0.2.0. The plugin is MIT; nothing it does changes.
  - `.obsidian/plugins/icor-for-life-outliner/manifest.json`: the version.
- **PDF Annotation 0.2.0 inside** (1.32.0 carried 0.1.3). The released
  assets byte for byte: `main.js` dc2bf55c9d35, unchanged since 0.1.3,
  `manifest.json` a5f9948e1056, `styles.css` 7cb2ad3a3d7c, from release
  0.2.0. The plugin is MIT; nothing it does changes.
  - `.obsidian/plugins/icor-for-life-pdf-annotation/manifest.json`: the
    version.
- **Planner 0.16.0, Connect 0.16.0, Focus 0.7.0, Interface 0.8.0, Scaffold
  Check 0.6.0, SQLite Viewer 0.6.0, AI Chat 0.16.0, Terminal 0.2.0,
  Canvases 0.4.0 and Scratchpad 0.2.0 inside**, each staged by the
  download from its own repository at that release. Docs-only releases:
  the `LICENSE` in each plugin folder is MIT, `main.js` is byte-identical
  to the previous release wherever the plugin ships a built bundle.

### Removed

Nothing. No file is removed, moved or renamed in this release.

### If you are updating by hand

Copy `06 AI Team/AI Team Knowledge/Scripts/LICENSE`, `LICENSE.md` and
`README.md`. Plugins update themselves from the community directory, or
copy each plugin folder from the download.

## 1.32.0 (2026-09-18)

The workbench you are handed is empty. `03 WiP/` is your room, and the
Scaffold now proves at release time that it ships the four buckets, their
`README.md` files and nothing else, so an update can never hand you a
half-finished piece of somebody else's work to wonder about.

Minor bump: one new check in a script that already ships. Two files
change, both of them scripts, and both are named below. Nothing is
removed, moved or renamed, nothing you wrote changes, and the new check
cannot fail a vault you are working in.

### Added

- **`validate-scaffold.py` check 16: the `03 WiP/` buckets ship empty
  except their `README.md`.** Any other file under `03 WiP/` fails the
  release, named in the failure line. Dotfiles are allowed, because
  `03 WiP/_archive/.gitkeep` is one, and empty folders are allowed,
  because `Workstreams/` and `Projects/` hold a named folder each.

  **It cannot fail your vault.** The check runs only in the repository the
  release is built from, which it recognises by a file that ships in no
  release. Anywhere else it reports itself `SKIPPED` on stdout and in
  `--json`, and is never counted as passed. A full `03 WiP/` in your vault
  is the room doing its job.

  Why a check rather than a note to self: the buckets were created on
  2026-09-17 and within hours a session wrote a hire workup into a folder
  of its own under `03 WiP/`. It was never committed, never in a manifest
  and never in a release, so it reached nobody, but nothing in the repo
  would have stopped it either. Four cases in `run-red-tests.py` hold the
  check to it, two red and two green, and the two green ones are the point:
  a dotfile is not a leftover, and a vault in use is not a failure.

### Changed

- **`06 AI Team/AI Team Knowledge/Scripts/validate-scaffold.py`** carries
  check 16 and names it in the header list. In your vault the only visible
  difference is one extra line, `SKIPPED check 16 (03 WiP buckets ship
  empty)`, telling you the check did not apply here. That line is the
  point: a check that cannot run says so rather than passing quietly.
- **`06 AI Team/AI Team Knowledge/Scripts/run-red-tests.py`** carries the
  four cases that hold check 16 to its job. The suite total moves from 440
  to 444.

### Removed

Nothing. No file is removed, moved or renamed in this release.

### If you are updating by hand

Copy the two scripts named above from this release into
`06 AI Team/AI Team Knowledge/Scripts/`. That is the whole update: no
folder is added, no note changes, and nothing has to be regenerated.

## 1.31.0 (2026-09-17)

The team grows from nine agents to ten. Ada is the planning and audit
specialist: before a piece of work that needs three or more agents, or
has real dependencies between its steps, she writes the plan Larry
dispatches from, and on request she audits the team's own machinery for
drift. Around her, a hire now runs its own scripts, the root contract
says which model runs what, the two hire scripts agree on which vault
they are in, and four of the bundles inside are newer than the ones
1.29.0 carried: the Connect, Interface and Planner plugins and the
INKLINE theme.

Minor bump: one agent is added with her contract, bio, journal, avatar
and three dispatch shims; `AGENTS.md` gains one section and one
sentence; `GL-1002` gains one optional key; `SOP-1007` gains one section
and two reworded steps; five scripts change. Nothing is removed, moved
or renamed, and a vault that already runs 1.30.0 keeps every file it
has after this update.

About 1.30.0: its tag sits on `65feac0`, a commit that carries only the
1.30.0 manifest rebuilt on the 1.30.0 tree. The manifest committed with
the version bump described three scripts as they were being edited for
this release, not as 1.30.0 shipped them, and the release gate refuses
a stale manifest. Nothing else in 1.30.0 changed. 1.30.0 has a tag and
no download: its release run started one minute before the 1.31.0 tag
was pushed, and the builder, re-reading the tags from GitHub mid-run,
found a version its manifest could not know about and refused. A tag
never moves, so 1.30.0 stays a tag, and this release is the first one
a member on 1.29.0 can download.

### Added

- **Ada, the planning and audit specialist.** Same two-file shape as
  the other agents (`SOP-1007`), a journal, a dispatch shim per host
  and an avatar in the INKLINE style. She produces two kinds of
  document and nothing else: a plan (steps, owners, dependency graph as
  a diagram, gates in order, risks, acceptance criteria) and an audit
  report (severity, re-runnable evidence, a negative-control note). She
  never dispatches an agent, never fixes what she audits and never runs
  a script that writes. Below three agents and without a real
  dependency between steps she says "under the floor, route inline" and
  stops. A release of your own plugin or theme is not hers either: that
  stays with you as maintainer, with Flint's review-before-ship read.
  - `06 AI Team/Agents/Ada/AGENT.md`: the contract.
  - `06 AI Team/Agents/Ada/Ada.md`: the bio.
  - `06 AI Team/Agents/Ada/Journal/_template.md` and
    `06 AI Team/Agents/Ada/Journal/2026-09-17-ada-hired.md`.
  - `.claude/agents/ada.md`, `.codex/agents/ada.toml` and
    `.gemini/agents/ada.md`: the dispatch shims, generated.
  - `06 AI Team/AI Team Knowledge/Avatars/ada.png`: the avatar.
  - `agent-index.md`, `AGENTS.md`, Larry's contract and `GL-1002` name
    the new agent. Larry's contract says when a request goes to Ada
    first, and that a step she did not name is a plan change that goes
    back to her, never an improvisation.

- **"Which model runs what", a new section in `AGENTS.md`.** Where the
  host lets Larry pick a model per dispatch, judgement work (a plan, an
  audit, a hire, a ruling, a review) goes to the strongest model the
  host offers and mechanical work to the default. The sorting test is
  the one in `GL-1005`. It is a preference, never a requirement: where
  the host offers one model, everything runs on that one, and no
  contract or shim in this Scaffold names a model or a vendor.

- **`tools`, an optional key on an agent contract (`GL-1002`).** A comma
  list of the tools the agent may use, each from the allowlist
  `check-hire.py` check 11 reads; absent means the host default. Ada's
  contract is the first to carry it (Read, Write, Glob, Grep, Bash: no
  edit in place, no dispatch), and the generator copies it into her
  shim.

- **"Scripts Nolan runs in a hire", a new section in `SOP-1007`.** A
  hire now runs end to end without you launching anything: Nolan runs
  `new-agent.py`, `scaffold-init.py plan` then `apply`, and
  `validate-scaffold.py` then `check-hire.py`, from the vault root, and
  shows every report at the approval step. That closed list is the one
  exception to "nothing here auto-launches", and `AGENTS.md` points at
  it rather than restating it. One hard stop inside it: a hire never
  changes the hook config. If `plan` lists `.claude/settings.json`,
  `.claude/settings.README.md` or `.codex/hooks.json` under CREATE or
  UPDATE, or prints a PROBLEM line, Nolan does not run `apply`; he
  reports the line and you run `apply` yourself after reading
  `Scripts/hooks-rules.json`.

- **Red case 15l in `run-red-tests.py`.** The hire scripts must refuse
  to write the public skeleton into a private vault, and `new-agent.py`
  must refuse to run at all without `check-hire.py` beside it. Watched
  red before it went green, like every case in the suite.

### Changed

- **`new-agent.py` and `check-hire.py` ask one function which vault
  this is.** `vault_is_public()` lives in `check-hire.py` and
  `new-agent.py` imports it. Until now the two scripts tested different
  things and could disagree, and `new-agent.py`, testing the manifest
  alone, wrote the public skeleton into a vault that was not the public
  Scaffold. With no `check-hire.py` beside it, `new-agent.py` now
  refuses rather than guess.
- `expansion-pack.py` counts Ada among the core agents an expansion
  pack can never overwrite, and `test-expansion-pack.py` proves it.
- `SOP-1007` steps 6 and 7b say Nolan runs the generator and the
  validators and shows the output; the Codex sandbox caveat stays.
- `.codex/config.toml` is re-rendered for the larger `AGENTS.md`
  (14,268 bytes, under the 32 KiB Codex budget).
- **Connect 0.15.1 inside** (1.29.0 carried 0.15.0). The "Auto-reveal
  current file" button is back in the file-explorer toolbar: one rule
  in the plugin's stylesheet hid it together with a button that no
  version of Obsidian puts there, and auto-reveal has no command to
  fall back on, so hiding the button took the setting away. "New note"
  now stays hidden under a non-English Obsidian too, matched by its
  icon rather than its English label.
- **Interface 0.7.0 inside** (1.29.0 carried 0.6.5). A command, "Toggle
  auto-reveal current file in the file explorer", bindable to a hotkey,
  and a switch under "Obsidian's interface" in the plugin's settings.
  Both read and write Obsidian's own setting, so nothing new is stored.
  That one feature needs Obsidian 1.8.3 or newer, where the setting
  arrived; on an older Obsidian the row says so and the command is not
  offered, and the rest of the plugin still runs on 1.5.0 and up.
- **Planner 0.15.1 inside** (1.29.0 carried 0.15.0). A data-safety fix,
  so it is worth knowing it arrived: starred email notes are no longer
  moved to the trash when a mailbox renumbers. If you star notes out of
  your mail, this is the version that stops losing them.
- **INKLINE 1.6.2 inside** (1.29.0 carried 1.6.1). The theme the whole
  vault is styled with. Nothing you have to do; it comes with the
  download.

  Both of these were in the 1.31.0 download and this section did not say
  so until 1.32.0. Added here rather than under 1.32.0, because the
  version that shipped them is the version that has to name them.

### Removed

Nothing. No file is removed, moved or renamed in this release.

### If you are updating by hand

Copy `06 AI Team/Agents/Ada/` and
`06 AI Team/AI Team Knowledge/Avatars/ada.png` from this release, then
run `scaffold-init.py plan` and `apply` from the vault root (on Windows
`py -3` in place of `python3`) so the three shims are generated rather
than copied. Replace `AGENTS.md`, `06 AI Team/Agents/agent-index.md`,
`06 AI Team/Agents/Larry/AGENT.md`, `GL-1002`, `SOP-1007` and the five
scripts named above. The three plugins come with the download: copy
their folders under `.obsidian/plugins/`, and the INKLINE theme folder
under `.obsidian/themes/`.

## 1.30.0 (2026-09-17)

The workbench gets topic folders. Work in `03 WiP/` no longer lands as one
dated folder among dozens; it goes into one of four buckets first, and is
dated inside it. Every bucket explains itself in its own `README.md`.

Minor bump: two folders are added and a handful of notes and two scripts
learn about them. Nothing is removed, moved or renamed, no work in your
own vault has to move, and a vault that already runs 1.29.0 keeps every
file it has after this update.

### Added

- **`03 WiP/Operations/` and `03 WiP/AI Team/`, two new buckets.** Together
  with the two that already existed, `03 WiP/Workstreams/` and
  `03 WiP/Projects/`, they are the four places work can go. You read them
  from the top of the list and stop at the first one that fits, which is
  what stops two people filing the same work in two different places:

  1. `Workstreams/<Name>/` for one run of a process that repeats.
  2. `AI Team/` for work on the team itself, a hire, an SOP, a script.
  3. `Projects/<Project note name>/` for work a Project note names.
  4. `Operations/` for everything else that keeps things running.

  `Operations/` is the one to know about. It takes bounded work that has
  no Project note, and it never asks you to open one. It is also the
  bucket that goes stale, because nothing closes it from the outside, so
  the checkpoint reads it first.

- **A `README.md` in every folder of the workbench**, written for someone
  seeing it for the first time: what goes in, what does not, two example
  names, and when a piece of work is a file and when it is a folder. New
  files: `03 WiP/Operations/README.md`, `03 WiP/AI Team/README.md` and
  `03 WiP/_archive/README.md`.

- **The one file or one folder rule**, inside a bucket. One file is
  `YYYY-MM-DD-<slug>.md`. Two files or more is `YYYY-MM-DD-<slug>/`. A
  single file that grows a second file becomes a folder of the same name,
  with the first file moved in as its `README.md`.

- **One command line per system, wherever you are asked to type one.** On
  Windows, `python3` opens the Microsoft Store instead of running
  anything, so the member-facing commands now show `py -3` for Windows
  beside `python3` for macOS and Linux (`README.md`, `AGENTS.md`,
  `WS-1006`, `SOP-1017`). The scripts in this vault need Python 3.9 or
  newer and nothing else: no install step and no packages, and `README.md`
  now says so.

### Changed

- `03 WiP/README.md` is rewritten around the four buckets: the order they
  are read in, what each one takes, the file or folder rule, and why two
  of them hold a named folder per process or per Project instead of dated
  work. The Workstream versus Project explanation is kept in full.
- `03 WiP/Projects/README.md` and `03 WiP/Workstreams/README.md` point at
  the bucket order instead of repeating it, and both drop the loose file
  allowance in favour of the dated file form.
- `Scripts/checkpoint.py` knows the buckets. A bucket is never offered for
  archive; the dated work inside it is, whether that work is a folder or a
  single `.md` file. A bucket's own `README.md` is never offered. The
  report lists `Operations/` first.
- `Scripts/validate-scaffold.py` requires the two new folders, so a vault
  missing them is reported. `.icor-for-life/manifest.json` reads that same
  list, so the rooms it names gain both.
- `SOP-1006`, `WS-1004`, `WS-1005`, `GL-1001`, `GL-1002`, `GL-1004`,
  `GL-1007`, `AGENTS.md`, `README.md` and `06 AI Team/README.md` all say
  where work goes in the same words, and link to `03 WiP/README.md` rather
  than restating the rule.
- `Scripts/new-progress-report.py` says in its help that `--wip` takes the
  path inside `03 WiP/` with the bucket included. Its behaviour is
  unchanged.

### Removed or moved

Nothing was removed, moved or renamed in this version.

### If you are updating by hand

Make the two folders, `03 WiP/Operations/` and `03 WiP/AI Team/`, and copy
the four `03 WiP/` README files from this release. Work already sitting in
`03 WiP/` can stay where it is: it archives from there as before, and the
buckets apply to what you start next.

## 1.29.0 (2026-09-17)

The Scaffold gets the security policy its twelve bundled plugins already had,
and the Planner inside it stops being able to undo work you did in Todoist or
ClickUp.

Minor bump: one file is added at the root and a bundled plugin gains two
features. No scaffold script, note, skill or hook changes, nothing is removed,
moved or renamed, and a vault that already runs 1.28.1 behaves the same after
this update apart from the Planner.

### Added

- `SECURITY.md` at the root of the Scaffold. It names one address,
  `support@myicor.com`, prefers a GitHub private advisory, and states what is
  in scope and what is not: in are the scripts under
  `06 AI Team/AI Team Knowledge/Scripts/`, the rendered `.claude/settings.json`
  and `.codex/hooks.json` that a runtime executes, the expansion-pack installer
  and its receipt model, and the release zip matching the commit it claims; out
  are the bundled plugins, each linked to its own repository, your own notes and
  credentials, and Obsidian itself. It also states the credentials posture
  plainly: the Scaffold ships no key, and both `.env` files you may hold are
  yours, git-ignored, and never inside the zip. Private vulnerability reporting
  is enabled on the repository, so the channel the document names exists.

### Changed

- **Planner 0.15.0 inside.** Two releases at once for anyone updating from
  1.28.1, which carried 0.14.2.

  From 0.14.3: a task you complete in Todoist or ClickUp can no longer be
  reopened by the planner. With Complete on source switched on, the planner
  marked the card done, then read its own note back a second later, decided the
  card looked unfinished, and set the task at the source back to the first open
  status it could find. The rule is now stated once and holds everywhere: the
  source always wins. What happens at the source is mirrored into your vault and
  never sent back out. Complete on source means exactly one thing, which the
  setting now says in full: checking a card here closes the task there, and
  unchecking a card you had checked reopens it. Nothing else crosses.

  From 0.15.0: a task deleted in Todoist or ClickUp now disappears from your
  vault too, into Obsidian's trash so you can bring it back, instead of leaving
  a note you could not open and could not get rid of and an "HTTP 404" every
  five minutes. The title of a task syncs both ways, the way the due date, the
  priority and the body already did, and if you rename it in both places between
  two syncs the source wins. Your own planning is never part of any of this: the
  day a card sits on, its half of the day, its order, the star for the week and
  the note you linked it to live only in your vault.

### Removed

Nothing. No file is removed, moved or renamed in this release.

## 1.28.1 (2026-09-16)

The wrapper that 1.28.0 stopped rendering is now gone from the tree, and the
ten script comments that still explained the retired environment prefix now
name the flags the rendered hooks actually carry.

Patch bump: one file is removed and everything else that changed is comment
text. Nothing a note, skill, hook or script points at moves, no field changes
meaning, and a vault that already runs 1.28.0 behaves exactly the same after
this update.

### Removed

- `06 AI Team/AI Team Knowledge/Scripts/session-start.sh` is deleted. Nothing has rendered it since 1.28.0, when the SessionStart hook began spawning session-start.py directly, and its one non-shell job, the plain line when the interpreter is missing, is now scaffold-init.py doctor.

  If you updated by hand and still have this file, delete it. Nothing reads it,
  nothing renders it, and a second entry point nobody maintains is how the
  Windows ritual failure got in.

### Changed

- Ten script comments that still explained sys.path isolation through the
  retired PYTHONSAFEPATH=1 prefix now name the -I -B -X utf8 flags the rendered
  hooks carry. Comment text only, no behaviour change. The remaining mentions
  of the variable are load-bearing: run-red-tests.py asserts the rendered
  blocks do not carry it, and scaffold-init.py and session-start.py explain in
  past tense why it could not do this job.

## 1.28.0 (2026-09-16)

The release that makes this Scaffold run on Windows. Seven defects stood
between a Windows member and a working harness, from an apply that died
halfway through to a red-test suite that could not start its first case, and
the hook lines themselves now render in a form Windows can execute without
Git Bash. Beside them, the bytecode and sys.path hardening across twenty
scripts, and the GL-1002 row that ends 47 false findings.

Reported by community member Conrad Fröhling, 2026-09-16.

Minor bump: GL-1002 row 55 changes, declaring the owner and uses that every
shipped SOP and Workstream already carries, and the rendered hook config
changes shape (exec form) for every member who runs scaffold-init.py apply,
which is a harness contract change. Nothing is removed, moved or renamed, and
every existing note stays valid as it is, so this is neither a major nor a
patch.

### Windows

- scaffold-init.py apply wrote host links before the skill files they point
  at, so on Windows without the symlink privilege the copy fallback had
  nothing to copy and apply died mid-harness. Files now come first, plan and
  apply share one order, a copy can satisfy check, and the summary says why
  the entries are copies.
- run-red-tests.py spawned /bin/sh in five places, which Windows cannot
  start, killing the suite before its first case. The shell is resolved once
  from PATH and the cases skip by name where there is none.
- scaffold-init.py doctor called every non-zero exit from the suite "RED", so
  a suite that could not run at all was reported as a guard letting bad input
  through. A crash and a red now read differently.
- session-start.py used select.select() on stdin, which Windows answers for
  sockets only, so the host's session id was never read and the ritual
  wrongly announced that the guards were off. A thread with the same timeout
  covers that platform.
- life-snapshot.py --write named os.O_NOFOLLOW unguarded and raised
  AttributeError on Windows before writing anything. The flag is optional
  now; the symlink refusals and O_EXCL still carry the protection.
- test-life-snapshot.py planted symlinks in six cases without checking
  whether the platform allows it. Those six skip by name, and the skip count
  rides on the summary line.
- Hook commands render in exec form (command plus args) with -I -B -X utf8
  and a braced ${CLAUDE_PROJECT_DIR}, so the guards run on Windows without
  Git Bash, where Claude Code falls back to PowerShell. The interpreter is a
  bare python3 on macOS and Linux and the absolute path to python.exe on
  Windows, so a synced folder carrying its own python cannot supply the
  guard; a Windows Python upgrade needs apply once more, and doctor says so.
  Below Claude Code 2.1.139, POSIX falls back to a shell form carrying the
  same flags and Windows refuses to render the hooks key and names the
  version to install. Run scaffold-init.py apply once after this update so
  the new hook lines land.
- The session start ritual is spawned directly as session-start.py and hands
  -I -B -X utf8 to every child; scaffold-init.py doctor names a dead
  interpreter in words. session-start.sh is no longer rendered and will be
  removed in a later release.

### Fixed

- Twenty scripts that load a sibling by path dropped __pycache__ into
  whatever tree they were pointed at, including a member's vault. All twenty
  now set sys.dont_write_bytecode. (Conrad Fröhling)
- Every guard drops its own folder from sys.path as its first statement, so a
  planted Scripts/json.py is inert however the guard was launched. (Vex)
- write-guard.py reads its payload as bytes and decodes UTF-8, so a note
  carrying an emoji is no longer a refused write on a Windows console. (Vex)
- check-bases.py no longer inserts its own folder at the front of sys.path
  for an import done by path. (Vex)
- check-quality.py and link-dates-to-daily-notes.py accept an escaped pipe as
  the alias separator, so the 17 table links in SOPs/INDEX.md no longer read
  as pointing at notes that do not exist. (Silas; the same reader bug Steven
  Koegler reported in the old myPKA validator)

### Guidelines

- GL-1002 row 55 declares owner and uses, the two fields every shipped SOP
  and Workstream already carries, ending 47 false invented-field findings.
  (Silas)

### Tests

Nine Windows red cases, three GL-1002 and alias cases, seven hook-shape
cases; the suite is 429 under Python 3.12 and 434 under 3.9 on a clean tree.

### Changed

- **Planner 0.14.2 inside.**

### Removed

Nothing. No file is removed, moved or renamed in this release.

## 1.27.0 (2026-09-16)

A release cut from one member's bug reports and from the two schema rulings
behind them. Eight defects in the scripts, five of them in the release suite
itself, and the rows in GL-1002 that finally declare what every version of
this Scaffold has actually shipped.

Reported by community member Brian Carroll, 2026-09-16.

Minor bump: GL-1002 changes rows that every note in the vault is checked
against, one of them a placeholder row that named a type no file uses and one
a type that was carried but never declared. Nothing is removed, moved or
renamed, and every existing note stays valid as it is, so this is neither a
major nor a patch.

### Fixed

- **`checkpoint.py`**: the cutoff for "tasks touched" is now when the session
  started (`.icor-for-life/scripts/session.json`), not the name of the newest
  session log. WS-1005 writes the report before the log, so the log's name
  belonged to the previous session: a task closed earlier in the same session
  vanished, and a task filed after the log was listed again by the next one.
  The log name stays as the fallback where no session start hook ran. Reported
  by Brian Carroll.
- **`check-quality.py`**: a bare `[[wikilink]]` now resolves to a candidate
  inside the scanned rooms before one outside them. A habit and its
  planner-habit note share a name by design, and the shorter `02 Planner/`
  path always won, so the member's own habit note was reported as an orphan.
  Reported by Brian Carroll.
- **`check-quality.py`**: agent journals (`06 AI Team/Agents/*/Journal/*.md`)
  are read; the glob is in scope, never the whole room. 0 findings on the
  shipped tree. Reported by Brian Carroll.
- **`planner-week.py`**: the week note's `created_at` uses an aware UTC `now()`
  instead of the deprecated `datetime.utcnow()`. Two new gates run the create
  path, and every script's `--help`, under `-W error::DeprecationWarning`.
  Reported by Brian Carroll.

### Guidelines

- **GL-1002**: the agent-journal row becomes `journal-entry`, with `agent_id`,
  `created` and `topic` required, matching every journal file the Scaffold has
  ever shipped.
- **GL-1002**: `agent-soul` is declared, the type Larry's `SOUL.md` has carried
  since 2026-08-28.
- **GL-1002 and `02 Planner/README.md`**: a habit and its planner-habit note
  link to each other by full vault path, because the two notes share a name by
  design. `new-entity.py` writes `planner_habit` qualified.
- **`new-agent.py`**: a hire's journal template carries its own `agent_id`
  instead of the first sibling's, which in this Scaffold was always charta.
- **SOP-1014**: two deterministic repairs for a vault upgrading into this
  release, one per stale journal template and one per bare habit link.

### Tests

- **`run-red-tests.py`**: the size-cap case builds its fixture instead of
  copying the vault, and dates its planted goal; with six or more open goals it
  went red on a member for whom the cap was working. Reported by Brian Carroll.
- **`run-red-tests.py`**: fixtures no longer copy `05 Assets`, `03 WiP` or
  `07 Databases`; thirty vault copies carried the member's binaries into one
  temporary directory, which made the suite unrunnable on a large vault. On a
  tree with 600 MB of assets the suite goes from 2:13 to 1:23. Reported by
  Brian Carroll.
- **`run-red-tests.py`**: red tests for three 1.24.0 fixes that shipped without
  one (a stamp summary with YAML metacharacters parsed back, `new-task.py move
  --to open`, `new-entity.py --set` on a defaulted and a commented field).
  Reported by Brian Carroll.
- **`run-red-tests.py`**: the four log-name checkpoint cases stop inheriting
  the live `session.json` from the vault they copy. Reported by Brian Carroll.

### Changed

- **Planner 0.14.1 inside.**

### Removed

Nothing. No file is removed, moved or renamed in this release.

## 1.26.0 (2026-09-15)

A Workstream is not a Project, and the vault now says so in three places:
the schema, the workbench and the team's own README. A Project is bounded and
ends; a Workstream is a repeatable process that never ends and carries a Goal
through the results it keeps producing. The workbench gains two standing
trees for exactly those two shapes, beside the dated deliverable folders.

Minor bump, additive. Two optional fields, two new folders with a README
each, one new rule in two checks. Nothing is removed, moved or renamed, no
field changes meaning, and every existing note stays valid as it is.

### Added

- **`03 WiP/Workstreams/` and `03 WiP/Projects/`, the two standing trees.**
  `Workstreams/<Name>/` is the standing working folder of a Workstream that
  runs continuously: the queue, the current run, one dated subfolder per run.
  `Projects/<Project note name>/` is the working folder of one bounded
  Project, linked from the note's `## Working folder` line. Both trees carry
  a `README.md` with the rules and one worked example each, and
  `03 WiP/README.md` gains the table that puts the three kinds of folder side
  by side: what each is, when it opens, when it closes, who links to it.
  Both folders are required rooms in `validate-scaffold.py`, the same way
  `03 WiP/_archive` is.
- **The Workstream as a goal carrier ([[GL-1002]] ruling 2026-09-15).** Two
  shapes were taught, a Project and a Habit; the third is a Workstream.
  `workstreams` on a `goal` (a wikilink list to the Workstream notes that
  carry it) and on a `project` (the Workstream a bounded project runs
  through), both optional; `wip_folder` on a `workstream` note, the standing
  folder, one string, set only when the folder exists. The working folder of
  a Project is deliberately not a field: its path is the note's own name and
  a derivable fact is not a field. `Templates/goal.md` and
  `Templates/project.md` carry the new key empty; `.obsidian/types.json`
  declares `workstreams` as `multitext` and `wip_folder` as `text`.
- **`06 AI Team/README.md` §"A Workstream is not a Project"**, one paragraph
  where the team already learns what the `Workstreams/` folder is for, with
  the filing test: one run of something that repeats, or a step toward a
  finish line.
- **`life-snapshot.py`: `goals.open[].carriers.workstreams`.** The report
  now names the Workstream carriers beside the Project and Habit ones,
  reading `linked_workstreams` and `workstreams` alike. Additive inside
  schema 1: the key is always present and empty when none, and
  `Scripts/README.md` now states the rule precisely (a rename, removal,
  retype or reorder is a new schema number; an added key is dated in the
  README). Five new fixture cases in `test-life-snapshot.py`, including the
  negative control that a Topic is never a carrier.

### Changed

- **`checkpoint.py` never proposes a standing tree as a candidate to
  leave.** `Workstreams/` and `Projects/` and every `Workstreams/<Name>/`
  are reported as `stand` and shielded; the dated runs and project folders
  inside them are scanned one level down under their prefix and can still
  be flagged, so the shield stops at the tree. Each `wip` row gains a
  `standing` boolean. Two red cases in `run-red-tests.py`: a 400-day-old
  `Workstreams/` must not be flagged, the 400-day-old run inside it must,
  and a vault without `03 WiP/Projects/` must fail `validate-scaffold.py`.
- `GL-1001` names the two standing trees in the `03 WiP` row; `GL-1002`'s
  ladder table reads "Project, Habit or Workstream" for the carriers.

### Removed

Nothing.

## 1.25.1 (2026-09-15)

Patch bump, one missing file: 1.25.0 shipped SOP-1017 and the scripts behind
it, but not the skill that opens it. Nothing in the vault is removed, moved or
renamed, and every part of 1.25.0 is in here unchanged.

### Fixed

- **`answer-the-six-life-questions` is now a generated skill, the way the other
  three already were.** SOP-1017 declares `skill_name:
  answer-the-six-life-questions` along with its triggers and its prerun, and a
  declared skill name is the whole input the generator needs. The generator was
  simply not re-run before 1.25.0 was tagged, so the release carried the
  procedure and the deterministic half without the door that reaches them: the
  six questions could be answered only by someone who already knew to open the
  SOP by hand, which is the one thing SOP-1017 exists to stop. Running
  `scaffold-init.py apply` created exactly three entries and changed nothing
  else: `06 AI Team/AI Team Knowledge/Skills/answer-the-six-life-questions/SKILL.md`,
  the canonical host-neutral copy, `.claude/skills/answer-the-six-life-questions/SKILL.md`,
  the Claude copy carrying that host's frontmatter and the inlined
  `life-snapshot.py --write --brief` prerun, and the per-device link under
  `.agents/skills/`, which is gitignored by construction and ships with no
  release. Both written files are byte-identical in shape to the three skills
  that shipped in 1.25.0, including the same host-versus-canonical divergence,
  so this is the file that was missing and not a new design.
- The gap was in the release, not in the generator. `scaffold-init.py plan`
  named the three creates on the first run, with no update, no removal and the
  eight hand-written shims correctly kept, which is the generator reporting a
  release that had been cut one step early.

## 1.25.0 (2026-09-15)

Six questions a member asks all the time, answered from one file a script
writes instead of from a walk through the folders: what are my goals, what
should I focus on, what are my weekly priorities, what is the highlight of
today, what are my key elements, what has my attention. Three of the six had
nowhere in the vault to live at all, so this release gives each of them a home
first, then the script that reads it, then the tables that show it.

Minor bump, additive. One new note type, three new scripts, five new Bases, one
new SOP and one new step in the session start ritual. Nothing is removed, moved
or renamed, no field changes meaning, and every existing note stays valid as it
is, so this is neither a major nor a patch.

### Added

- **`Scripts/life-snapshot.py` and the report it writes.** It reads the Goals,
  Projects and Key Elements rooms, the Journal months touching the last 30 days,
  the Planner and the scratchpads, and writes
  `.icor-for-life/scripts/snapshot.json` (schema 1, documented in
  `Scripts/README.md`). `--brief` renders about twenty lines a person reads,
  `--json` the whole report for a machine, `--write` puts it on disk. It never
  decides which projects are in focus and never picks a highlight: it reports
  what is recorded. A source with no data says so in `degraded` rather than
  being reported as empty, and a missing report means the script did not run,
  never that the life is empty.
- **`Scripts/planner-week.py` and the `planner-week` note type.** One note per
  ISO week at `02 Planner/Weeks/YYYY-Www.md` with two blocks: `## Weekly
  priorities`, a checklist of outcomes for the week, and `## Daily highlights`,
  one row per day using the habit log's own marker set. `ensure`,
  `add-priority`, `done-priority`, `set-highlight`, `mark-highlight` and `show`.
  It never proposes a priority and never picks a highlight, it never rewrites a
  line it did not come to change, and a CRLF note stays a CRLF note byte for
  byte.
- **`Scripts/set-property.py`**, one frontmatter property on one note, refusing
  a value outside the field's closed set, a field GL-1002 does not declare for
  that note's type, and any field a plugin or a sync owns. This is the setter
  behind `focus_rank`: a decision stored as data, written deterministically
  rather than by a model editing YAML by hand.
- **Five Bases for the My Life rooms**, with `new-base.py` registry entries
  behind them: `Goals.base`, `Projects.base`, `Key Elements.base`, `Topics.base`
  and `Habits.base`. Goals carry an Active view sorted by target date, Projects
  a Focus column and an Active view ranked by it. GL-1006's My Life row moves
  from "later candidates" to Base.
- **`focus_rank` on a project** (1, 2 or 3; absent means not in focus, at most
  three projects carry it). It stores your decision about what matters now.
  Nothing sets it from activity, and a fourth rank or a duplicate is reported
  as a finding rather than quietly corrected.
- **`linked_note` on a planner item**, plan-owned, one wikilink to a project
  note. It is the join that was missing: without it, planned and finished work
  can never be attributed to a project.
- **`SOP-1017 Answer the six life questions from the snapshot`**, the reading
  procedure for the report, including the line to say when the report is absent
  and the two places where a model may propose (a focus rank into an empty
  field, a retrospective highlight) and must then wait for your yes.
- **Step 6 of the session start ritual.** `Scripts/session-start.py` now runs
  `life-snapshot.py --write --brief`, so the six answers are already in front of
  the model before anyone asks. The brief is cut at 16000 characters and says
  when it was cut, because this output is printed into every session.

### Changed

- **GL-1002** gains the `focus_rank` and `linked_note` rows above, a `Planner
  items` section documenting the seven fields the Planner plugin writes, and a
  `Planner weeks` section holding the week-note concept. `weekly_goal` keeps its
  key and loses the word "goal" on every label: it pins an item to the week. The
  word "goal" stays with `type: goal` and only there, and the day sense always
  carries the word "Daily", because "highlight" already means a PDF highlight.
- **`02 Planner/README.md`** gains a Weeks paragraph, and **WS-1002 (the weekly
  review)** step 6 now writes the week's priorities through `planner-week.py`
  instead of into a session log.
- **`Scripts/README.md`** gains the reader contract for `snapshot.json`: refuse
  a file over 2 MB or a schema that is not 1, treat every string in it as
  untrusted display text, open a path from it only when the path is relative and
  inside the vault, report a stale stamp as stale, and cap what reaches model
  context to the brief.
- **`Scripts/run-red-tests.py`** gains the two cases named on the
  `session-start-ritual` row of `hooks-rules.json`, both watched go red before
  they were trusted: `life-snapshot-fixtures` (the fixture suite passes and its
  own `--break-me` proves it can still fail) and `life-snapshot-missing-report`
  (with the report and the script gone, the ritual prints the missing-file line
  and prints no goal list beside it), plus the case behind the size cap.

### Security

Three findings on the snapshot writer, all caught in review before it ever
shipped, so no released version of this scaffold ever carried them:

- The credential scan covered 6 of the 13 families the write guard refuses, so
  a Stripe-shaped value pasted into a checklist line would have been written
  into the report with exit 0. The guard's pattern list is now lifted verbatim
  and all three writers carry the same one.
- The write followed symlinks out of the vault. The temp file is opened
  `O_NOFOLLOW|O_EXCL`, the parent is resolved and checked, and a destination
  that is a symlink is refused. A refusal now happens before the temp file
  exists, so nothing is left behind.
- `.icor-for-life/VERSION` was copied into the report verbatim and unbounded.
  It is validated against a version shape now, never read through a symlink,
  and an unparseable one becomes `unknown` plus a degraded entry.

### Removed

Nothing. No file is removed, moved or renamed in this release.

## 1.24.1 (2026-09-15)

Patch bump, one defect: the release's own red-test gate crashed on the CI
runner, so 1.24.0 could not be published. Nothing in the vault itself changed,
and every fix listed under 1.24.0 is in here unchanged.

### Fixed

- **The red-test suite no longer writes Python bytecode into the fixture vaults
  it walks, it compares those vaults byte for byte rather than as UTF-8 text,
  and it names the interpreter it runs under.** The 1.24.0 run did not fail, it
  crashed: `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xcb in
  position 0`, which is the first byte of a `.pyc` magic number. The chain:
  `scaffold-init.py` loads its siblings by path, stock CPython compiles them and
  writes `__pycache__/*.pyc` beside them, which is inside the fixture vault, and
  the snapshot taken either side of the second apply then walked that fixture
  reading every file as UTF-8 text. Three fixes, because any one of them alone
  would have been a workaround. The write is stopped at the source:
  `PYTHONDONTWRITEBYTECODE=1` on the suite's own environment, which every child
  inherits, forced again at the spawn point so a caller-supplied env cannot drop
  it, plus `sys.dont_write_bytecode` for the suite's own importlib loads, which
  were dropping a `.pyc` into whatever tree the run was started from. The
  snapshot compares `read_bytes()`, so a fixture holding bytes nobody wrote on
  purpose is reported as a difference instead of raising on it, and bytes are
  the stricter comparison anyway. And every run prints the interpreter it is
  under: where that interpreter sets `sys.pycache_prefix`, which Apple's
  `/usr/bin/python3` does, the run says at the start and again in its own
  summary that it cannot see the defect class that crashed the 1.24.0 gate, and
  names the reason. A pass from a Mac can no longer read as a pass it did not
  earn, which is how this class reached CI twice. Filtering `__pycache__` out of
  the snapshot was the other option and was not taken: it hides this, and it
  hides any real difference standing next to it. The negative control then found
  a fourth thing. The refusal counted its differences with `zip()` over two
  sorted lists of different length, so a planted file that sorts last and shifts
  nothing read as "the second apply changed 0 file(s)". A refusal whose own
  count says nothing changed is a verdict contradicting itself, and under byte
  identity that message is the reader's only information. It compares by path
  now and names the files.
- The same treatment for the two other spawners. `check-hire.py`, whose
  `--self-test` copies helper scripts into a fixture vault and runs them out of
  it, and `test-expansion-pack.py`, whose children import siblings by path, both
  set `PYTHONDONTWRITEBYTECODE=1` on their own environment and pass it
  explicitly to every child they spawn.
- `Scripts/build-scaffold-manifest.py` sets `sys.dont_write_bytecode` for the
  same reason. It importlib-loads `mint-agent-ids.py` out of the repo's own
  `Scripts/` folder, so it was writing a `.pyc` into the very tree whose tracked
  files it hashes. Gitignored, so it never reached the manifest or the zip, and
  on the release path all the same.
- `1.24.0` was tagged at `087b332` and never published: every gate before the
  artifact was green on the maintainer's Mac, the suite crashed on the runner,
  so the draft step never ran and there is no 1.24.0 release to delete. The tag
  stays where it is, because a tag never moves. 1.24.1 is the same tree plus
  this fix.

## 1.24.0 (2026-09-15)

The first release cut from member bug reports end to end. Four members ran
1.23.1 in their own vaults and filed what broke; everything below is one of
their items, named by the item id they filed it under, and every fix carries a
case in `run-red-tests.py` or `test-expansion-pack.py` that was watched go red
against the old code before it landed.

Reported by community members Brian Carroll (T16), Andrew Gillley (T13),
Ian Slattery (T11 and T15) and Darshan Achar (T17), 2026-09-15.

Minor bump, additive: one new script, one new importable room, five refusals
an Expansion pack now meets that it did not meet before, and a long list of
script defects. Nothing is removed, moved or renamed, so no major and no
patch. The expansion-pack refusals would be a breaking change for a published
pack; no pack has ever been published, so there is nothing anywhere to break.

### Fixed: the scripts

- **T16-1** `Scripts/stamp-processed.py --archive` ran its checks AFTER it
  wrote the stamp. A note outside `01 Inbox/Outer World/` was left marked
  `processed: true` and not archived, and the second run refused it as already
  stamped, with no way forward that did not mean editing the frontmatter by
  hand. The checks now run before anything is written.
- **T16-19** `processed_summary` and each `processed_into` item went through an
  f-string between two bare double quotes, so a summary carrying a quote, a
  colon or a backslash broke the note's YAML while the script printed OK. Both
  go through `json.dumps` now: a JSON string is a valid YAML 1.2 double-quoted
  scalar, escapes and all.
- **T16-2, T13-6, T15-C** `Scripts/import-file.py` read `args.mtime_from`
  against a namespace called `a`, so every import raised `NameError` and exited
  1 AFTER the copy had landed: the file was imported, the manifest line was
  never written, and the caller read the run as failed. Fixed. `02 Planner`
  joins the importable rooms, because the Planner writes notes a member imports
  alongside everything else; `07 Databases` stays out, because nothing there
  has a markdown source.
- **T16-3** `Scripts/run-red-tests.py` read a case's exit code and nothing
  else, so a guard that writes first and refuses afterwards passed. It now
  hashes the files a case names before and after the run and fails on a changed
  byte. The `stamp-processed` cases pass their whole fixture vault to it, which
  is how T16-1 was seen.
- **T16-4** `Scripts/new-journal-entry.py` wrote `--original` through
  `.strip()`, which ate a deliberate leading indent or a trailing blank line out
  of the one section GL-1003 calls sacred. The member's words now land exactly
  as they were passed; the strip survives only in the empty-input guard, where
  it asks a question rather than changes the text.
- **T16-5** `Scripts/check-quality.py` counted a blank daily note as an
  unprocessed scratchpad. `link-dates-to-daily-notes.py --fix` creates an empty
  daily note for every day a link points at, on purpose, so a member who linked
  forty dates woke up to forty things to process and an oldest-unprocessed age
  measured from a note nobody had written in. Nothing to process is nothing to
  report, and it stays out of the oldest-unprocessed clock too. A scratchpad
  that does have a line in it still fires.
- **T16-6** The same script's wikilink resolver took the FIRST file the walk
  handed it, so `[[Notes]]` resolved to whichever `Notes.md` `os.walk` reached
  first and the answer changed when a folder was renamed beside it. It takes
  the shortest path now, which is what Obsidian does, with the path string as
  the tie breaker so the answer never depends on walk order. It also never read
  `aliases`, so every link written to an alias, which is the entire purpose of
  an alias, was reported as dangling. Aliases are indexed last and never
  displace a real filename: a note is its name first.
- **T16-7** And it counted a wikilink inside a code fence or an inline span as
  a link, so every guideline that teaches wikilinks read as one of the notes
  with the most dangling links in the vault. Code is blanked, not deleted,
  before the link scans, so every finding still points at the right line. The
  frontmatter stays in scope: a wikilink in a `topics:` list is a real link.
- **T16-10, T15-B** `Scripts/new-entity.py --set` matched `^field:[ \t]*$` and
  nothing else, so it could only fill a template line that was completely bare.
  Seven of `Templates/note.md`'s own fields are not bare. A line now counts as
  fillable while its value is empty, `[]` or `false`, whatever comment follows
  it, and the refusal names the template line it is looking at. A field whose
  template default is a list is written as a list, so `--set tags=pkm` no longer
  lands a string where every reader expects a sequence. And the keys a template
  marks as belonging to another `note_type` are pruned, so a note copied from
  the union template no longer arrives with four meeting keys it will never use.
- **T16-11** `Scripts/link-dates-to-daily-notes.py` had one scope, the whole
  vault, so linking the dates in one processed scratchpad rewrote date mentions
  across three rooms as a side effect. `--path` takes a file or a folder and is
  repeatable. The collision scan still walks the whole vault, because a name
  clash anywhere is what makes `[[YYYY-MM-DD]]` ambiguous. `SOP-1001` now passes
  one `--path` per note the run created, never a bare `--fix`.
- **T16-12** `Scripts/checkpoint.py` compared every task's mtime against the
  last session log's FILESYSTEM mtime. A session log is named for the moment it
  covers, and that is the fact this scan needs; its mtime moves forward on a
  sync, a Time Machine restore, a checkout, or the member simply reopening the
  log to read it, and the cutoff then sits in the future and the report says
  `tasks touched : 0` on a session that shipped six of them. The timestamp is
  parsed from the filename, with mtime as the fallback for a log written by
  hand, and the last log is picked by that timestamp rather than by sort order.
- **T16-13** `Scripts/new-task.py move --to open` was rejected by the argument
  parser, which listed every state except the one a task comes back to when work
  is parked. Accepted now, and moving a task to the state it is already in says
  so instead of reporting a destination clash.
- **T16-15, T13-4** `Scripts/run-red-tests.py` built its content fixtures by
  copying the vault root and ran its clean control against that copy. In this
  repo that is the shipped example set and everything reads ok; in a member's
  vault it is the member's life, and a lived-in copy produced 9 FAIL and exit 1
  on a suite whose only value is being trustworthy when it fires. The fixture
  vault is now rebuilt empty from `validate-scaffold.py`'s own room list and
  seeded from the vault's own `Templates/`, so every count a case asserts is a
  count the suite put there. The live vault's health is printed as a NOTE that
  decides nothing.
- **T13-5** `Scripts/mint-agent-ids.py` and `Scripts/check-quality.py` passed
  `re.split`'s `maxsplit` positionally, which is deprecated since Python 3.13
  and printed a `DeprecationWarning` straight into the member's terminal. Passed
  by name now.
- **T15-A** A shared `Scripts/noteio.py` reads and writes member files as bytes,
  so a CRLF note, a stray lone CR and a note created on Windows keep their exact
  line endings through every script that edits them. Python's text mode is
  universal-newlines on the way in and platform-endings on the way out, so the
  ordinary read-edit-write shape quietly rewrote the endings of every note it
  touched, and nothing looked wrong on macOS until the member opened the same
  note on Windows, or in git, and read every line as changed. Adopted in
  thirteen scripts. A folder that holds one of those scripts without
  `noteio.py` beside it now refuses in one line naming the folder, instead of a
  `FileNotFoundError` out of `importlib` that nobody sees.
- Already shipped in 1.23.1, recorded here for the reporters: **T16-16**,
  **T16-18** and the frontmatter half of **T16-9** were fixed by commit
  `c21d17e`, and **T13-7**'s check was removed before that.

### Added

- `06 AI Team/AI Team Knowledge/Scripts/noteio.py` - one byte-safe reader and
  writer for member files, loaded by path so the import needs nothing on
  `sys.path`. `read_note(path)` returns the decoded text with nothing
  translated plus the line ending the file uses most, which is what a caller
  appends with when it ADDS a line; `write_note(path, text)` writes bytes, so
  whatever endings are in the text are the endings on disk.

### Security: expansion packs

Five findings from Darshan Achar's report (T17), all reproduced on 1.23.1,
all fixed here. Every one carries a case in `test-expansion-pack.py` that was
watched go red against the old code.

- **F1 (critical)** An Expansion pack can no longer install anything under
  `06 AI Team/AI Team Knowledge/Scripts/`. `Scripts` is out of the allowed
  target kinds with no allow-list, because the danger is the folder and not the
  file: every script the session start runs imports from there, and a stray
  `Scripts/json.py` shadowed the standard library for `expansion-pack.py`
  itself and locked `remove` out of its own vault. As a second layer, the
  session-start wrapper and every guard command rendered into a host's hook
  config export `PYTHONSAFEPATH=1`, so the script's own folder is off the front
  of `sys.path` for the scripts that run at every session start. The variable
  and not the `-P` flag on purpose: Python before 3.11 ignores the variable and
  hard-errors on the flag, and an old interpreter must degrade rather than stop
  a guard from running at all.
- **F2 (high)** A pack target or payload source is refused if any path segment
  is `__pycache__`, case-folded, or the final segment ends in `.pyc`, `.pyo`,
  `.pyd`, `.so`, `.dylib`, `.pth`, `.plist`, `.pyw` or `.egg-link`. The refusal
  names the suffix.
- **F3** An `06 AI Team/Agents/` target whose folder name differs only by case
  from a folder already in the vault is refused, compared against the real
  directory entries rather than against the nine core names, and the message
  names the existing folder.
- **F4** Every pack-installed SOP, Workstream, Guideline or Template must carry
  a namespace prefix, the pack id followed by a hyphen or `EP-`, so a pack
  cannot ship a file that reads as the scaffold's own numbered knowledge.
- **F5 (high)** The install receipt moved out of the pack to
  `.icor-for-life/expansions/<pack-id>.json`, written with exclusive creation so
  an existing one is never overwritten in silence. `list` and `remove` read only
  from there and ignore any in-pack `installation.json`; `install` refuses a
  pack folder that already ships an `installation.json` or a `removed-*.json`;
  `remove` renames the receipt to `removed-<timestamp>.json` beside it and still
  verifies every listed file's sha256 first. `GL-1012` and `WS-1006` describe
  the model, and `check-hire.py` check 22 reads the new location and nothing
  else. It has no fallback to the old in-pack path, on Vex's ruling: no pack has
  ever been published, so no legacy install exists anywhere, and a second reader
  of a file the pack itself ships is the thing F5 exists to forbid.

### Fixed: Windows

Reported by Ian Slattery (T11), from running 1.23.1 on Windows.

- **T11-1** `Scripts/open-in-obsidian.py` opens the `obsidian://` URI with
  `os.startfile` on Windows. Its fallback looked for `open` or `xdg-open`, and
  Windows has neither, so the script exited 3 and every stop of the `WS-1003`
  guided tour failed there. The new branch is also what `--dry-run` prints.
- **T11-2** It finds the Obsidian CLI as `Obsidian.com` and in the two Windows
  install roots, not only as `obsidian` on PATH. On Windows the executable has
  the other name and is not on PATH at all until the member turns the CLI on in
  Settings, so the script reported "no Obsidian CLI" on every Windows machine
  that had one. The recommendation names the Settings toggle.
- **T11-3** The CLI requirement reads Obsidian installer 1.12.7 or newer
  everywhere, in the docstring, in the recommendation and in `WS-1003`. The old
  "Obsidian 1.12+" was wrong on every platform: the CLI arrived with that
  INSTALLER version, and the installer version is not the app version the member
  reads in Settings, so a member on a newer-looking app could be missing the CLI
  with no way to find out why. `WS-1003` now says the two numbers are different
  rather than leaving the reader to discover it.

### Documentation

- **T11-4** Member-facing documents spell the Windows key on first use,
  `Cmd+N (Ctrl+N on Windows)`, short form afterwards, with the convention stated
  once in `GL-1010`'s key table. Seven documents needed it, not the four in the
  report: `GL-1007`, `SOP-1004` and `SOP-1005` carried a bare `Cmd+O` as well.
  `run-red-tests.py` gains the sweep that found them, and it skips by name
  outside this checkout, because a member who writes `Cmd+K` in a note of their
  own is not a defect in this repo.
- `GL-1012`, `WS-1006` and `06 AI Team/Expansions/README.md` describe the tool
  that exists after F1 to F5 rather than the one that did before. `Scripts`
  payloads are not supported in schema 1, full stop; the old "needs a source
  review and explicit approval" paragraph is gone, because it described a gate
  that cannot hold. The "additive, non-executing" framing is corrected wherever
  it implied that a copied file is inert: `executes_payload: false` is kept and
  now says what it means, which is that this tool runs nothing from the pack. It
  has never meant that nothing installed can run.

## 1.23.1 (2026-09-15)

Patch bump, one defect: the member zip was not reproducible on the CI runner,
so 1.23.0 could not be published. Nothing in the vault itself changed.

### Fixed

- **The member zip is a function of the commit again, on the runner as well as
  on a Mac.** The release workflow builds the zip twice, once as a dry run and
  once from the tag, and refuses to publish unless the two are the same bytes.
  It went red twice on 1.23.0 with four distinct hashes. The cause: the
  release's red-test gate runs the suite against the staged tree, the suite
  imports three of the tree's own scripts with `importlib`, CPython writes
  their `__pycache__/*.pyc` next to them inside that tree, and a `.pyc`
  embeds the absolute path of its source, which is a `mktemp` directory whose
  name ends in six random characters. Three entries of the zip therefore
  changed on every build. It was invisible on the maintainer's Mac, where
  Apple's `/usr/bin/python3` redirects the bytecode cache to
  `~/Library/Caches/com.apple.python` and the files never reached the tree at
  all. Three locks, in order of strength: the red-test gate now runs against a
  byte-identical COPY of the staged tree, so nothing a gate does can reach the
  bytes that ship; the staged tree is hashed either side of that gate and a
  single added or changed byte blocks the build; and compiled bytecode
  anywhere in the tree blocks the zip outright, rather than being filtered out
  quietly, because a filter hides whatever ran inside the bytes.
- `1.23.0` was tagged at `c21d17e` and never published: every gate before the
  artifact was green, the reproducibility comparison went red, so the draft
  step never ran and there is no 1.23.0 release to delete. The tag stays where
  it is, because a tag never moves. 1.23.1 is the same tree plus this fix.

### Added

- `06 AI Team/AI Team Knowledge/Scripts/zip-staged-tree.sh` - the part of the
  builder that turns a staged tree into bytes, in its own file for the same
  reason the red-test gate is: `build-release-zip.sh` needs a git mirror, the
  gh CLI and the network, so a red test cannot call it. Four new cases in
  `run-red-tests.py` build a fixture tree twice under two locales and two
  clocks and assert one sha256, and plant the bytecode that must block and
  watch it block.
- `ICOR_ZIP_DEBUG_DIR` on the builder: a listing of the staged tree (sha256
  and path) at three points, plus the finished zip's per-entry listing. Like
  `ICOR_ZIP_SELFTEST` it can only ever add output, never turn a failing gate
  green.
- `ICOR_ZIP_SELFTEST=stage-write`: plants a file in the staged tree after it
  was hashed, so the new assertion can be watched going red. It was.
- The release workflow keeps both zips and both entry listings as run
  artefacts on every run, red or green, and diffs them into the log.

## 1.23.0 (2026-09-15)

The harness layer starts here. The rules a machine can check stop being prose
and become guards, and every host binding is generated from the vault's own
frontmatter instead of typed into a config by hand. Every guard carries a red
test and a written statement of what it does not prove.

Minor bump, additive: one generator, a canonical home for skills, six new
scripts, hook configs and agent shims for three more hosts, one new SOP and
two rewritten ones, five new frontmatter fields, and one slash command that
became a skill of the same name.

Three pilots ran this version as a member would, on Claude Code 2.1.270 and
Codex CLI 0.154.0: capture a note, checkpoint and resume, and hire a
specialist. Everything under Fixed is something one of them watched go wrong
on a real fixture, most of it on the host with the weaker guard surface, and
every fix carries a red case in `run-red-tests.py` that was watched go red
before it landed.

### Added

- **The generator, `06 AI Team/AI Team Knowledge/Scripts/scaffold-init.py`.**
  Four verbs: `plan` prints every file it would create, update or remove and
  writes nothing; `apply` writes them; `check` fails when a second apply would
  change anything or when a generated file was hand-edited; `doctor` says, per
  host, what is detected, installed, trusted, tested and unsupported. Nobody
  writes a host file by hand again: skills come from the SOP's or Workstream's
  own frontmatter, agent shims from the contract's, hook configs from
  `hooks-rules.json`. Every generated file opens with a header naming its
  source and carrying a content hash, and only a generated file whose source
  is gone is ever removed. It finds the scaffold root by walking up to
  `AGENTS.md`, never through git, because a member's vault is a plain folder.
- **The canonical skills home `06 AI Team/AI Team Knowledge/Skills/`**, with
  three generated skills in it: `checkpoint` (from `WS-1005`), `import-skill`
  (from `SOP-1012`) and `red-tests` (from `SOP-1016`). The skill is a pointer
  and the procedure is the body, so procedure text is never copied into a
  `SKILL.md`. The `.claude/skills/` copies are adapters carrying the
  Claude-only frontmatter and the injected prerun; `.agents/skills/` holds the
  links that Codex, Gemini CLI and Cursor read.
- **`06 AI Team/AI Team Knowledge/Scripts/hooks-rules.json`** (`schema: 1`):
  one host-neutral table of every guard rule, its event, what it matches,
  which script answers it, its severity, its unlock and what it does not
  prove. Each host's hook config is rendered from this table, so a matcher
  typed into a host config by hand is host lock-in and is now a defect.
  Adding a host is one entry under `host_matchers`, never a sweep through the
  rules. The `codex` entry is verified against OpenAI's own hooks
  documentation: twelve events, the same config shape, exit 2 to deny, and
  matcher aliases where `Edit` and `Write` both match a file edit.
- **`Scripts/session-start.sh` and `Scripts/session-start.py`**: a SessionStart
  hook that runs steps 0, 3 and 5 of the session start ritual
  (`check-onboarding.py`, `check-quality.py --write` when `quality.json` is
  stale, `expansion-pack.py list`) and puts the results in front of the model
  instead of asking it to fetch them. Where python3 is missing it prints one
  plain line and the session still starts.
- **`Scripts/write-guard.py`**: a PreToolUse guard on the file-writing tools.
  It refuses a write to `00 Daily Scratchpad/`, to root `AGENTS.md` or
  `CLAUDE.md`, or to a specialist `AGENT.md`, and refuses any write carrying a
  secret-shaped value (hard rules 1, 3 and 10, enforced for the first time).
  `ICOR_UNLOCK_WRITES=1` lifts it for one call, and the unlock has its own red
  test.
- **`Scripts/skill-doctor.py`**: reads every skill in the vault and checks the
  name, the description and its trigger phrase, the body length, the single
  pointer, the generated header, host-only frontmatter in the wrong place, em
  and en dashes, a clash with a remaining slash command, and the total
  description budget the host spends on skills before a session starts.
- **`Scripts/new-agent.py`**: the scripted half of a hire. It creates the
  agent folder, the contract skeleton, the bio card, the `Journal/` with its
  template and first entry, mints `myicor_id` through `mint-agent-ids.py` so
  one script owns identities, and adds the agent-index row. It writes
  skeletons with blanks in them and never the words, never a shim and never a
  `SKILL.md`: those are generated. It refuses to run without a deliberate
  unlock, and refuses to overwrite a contract that already exists.
- **`Scripts/check-hire.py`**: twenty-two checks that refuse an incomplete
  hire, from the folder shape and the frontmatter through the identity, the
  bio, the avatar, the journal and the shim, to whether the shim points at a
  contract path that exists. A shim pointing at a missing path used to fail
  silently at dispatch time, months later, as "the agent did not answer".
- **`Scripts/release-gate-red-tests.sh`**, called by `build-release-zip.sh`:
  no release while any guard in the tree about to ship did not refuse what it
  must refuse. Build tooling, stripped from the member download like the
  builder itself.
- **`06 AI Team/AI Team Knowledge/SOPs/SOP-1016-run-the-red-tests-and-gate-a-release.md`**:
  how the team watches a guard go red, and how the same suite blocks a build
  while any guard has not. A `SKIP` is not a pass and the count is reported
  with its skips every time.
- **The host adapters, all generated**: `.claude/settings.json` with
  `.claude/settings.README.md` beside it, `.codex/agents/*.toml` (Codex
  subagents are TOML and their prompt lives in `developer_instructions`),
  `.codex/hooks.json`, `.codex/config.toml` (raising `project_doc_max_bytes`),
  `.gemini/agents/*.md`, `GEMINI.md`, and the `.agents/skills/` links. Cursor
  gets nothing on purpose: it reads Claude Code's skills, agents and hooks.
- **`Journal/` for all eight shipped agents**, each with the journal template
  and a first entry, so a durable insight has a home from the first session
  rather than after the first hire.
- **Five frontmatter fields, in `GL-1002-frontmatter-conventions`.** On an SOP
  or a Workstream: `skill_name`, the skill's folder slug, required as soon as
  `skill_triggers` is non-empty. A slug derived from the title would break
  every host link the first time the title was reworded, with no error
  anywhere, so the name is a field somebody decides rather than something the
  generator guesses. On an agent contract: `routing_description` (required on
  every new hire, the one source for every host shim's routing text),
  `shim_reads`, `owns_gates` and `brief_waived`.

### Changed

- **`checkpoint.py`**: `--assert-logged` now reads a completion receipt for
  THIS session (`.icor-for-life/scripts/receipts/<session-id>.json`,
  `schema: 1`: workflow, session, started and finished, input and output
  hashes, validator version, unresolved items) written by the new
  `--write-receipt`. It used to pass on any session log dated today, so a log
  written in the morning closed an afternoon session that wrote nothing.
  `--assert-logged-today` keeps the old check under its true name, documented
  as weaker. `WS-1005-checkpoint` gains the receipt step.
- **`check-bases.py`** reads `.base` files with the standard library only. It
  was the one script here that imported PyYAML, and on a python3 without it
  two red-test gates reported a failed guard when the guard had never run. The
  reader is strict, and a red test compares it with PyYAML on every shipped
  `.base` wherever PyYAML is present, so it cannot drift from real YAML
  unnoticed.
- **`run-red-tests.py`**: a case that must be refused plus a clean control for
  every new guard, including the unlock, the missing-python path, the receipt
  that belongs to another session, the release gate refusing on a red, and
  five cases for the generator watched go red against a deliberately broken
  copy of it. One of those five is a control that stops another passing for
  the wrong reason: a shim carrying nothing the contract does not must be
  replaced, or "a shim with extra instructions survives" would pass on a
  generator that never replaced anything.
- **`SOP-1007-hire-a-new-agent`** is rewritten around the two scripts: the
  hire is `new-agent.py`, then the words, then the generator, then
  `check-hire.py` exiting 0 before the hire is announced.
  **`SOP-1011-import-or-align-an-external-agent`** and
  **`SOP-1012-convert-an-external-skill`** follow the same shape, and
  `WS-1006-install-an-ai-team-expansion` and `GL-1012-ai-team-expansions` name
  the generator where they used to describe host files by hand.
- **The eight shipped agent contracts** carry `routing_description`, so the
  `.claude`, `.codex` and `.gemini` shims are rendered from the contract
  rather than written twice. `Agents/Agent 01/` documents the new fields for
  the next hire.
- **`06 AI Team/README.md`** names the new `Skills/` room.
- **`AGENTS.md`** describes the harness layer where it describes the runtime:
  skills, agent shims, hook configs and host pointer files are generated from
  the vault's own frontmatter by `scaffold-init.py`, a skill is a pointer to
  its SOP, a guard is a hook where there are hooks and a prose rule where
  there are none, and the dot folders are per device and never the source of
  truth. The session start ritual and the checkpoint now both say the same
  thing to a member whose host has no hooks and no commands: run the scripts
  yourself.
- **`ADAPTER-PROMPT.md`** is generator-aware. The prompt asks the model to
  name its host and the capabilities it actually has, to report which harness
  folders exist, and, when the harness is missing or stale, to print
  `scaffold-init.py plan` and stop rather than run anything. `README.md` step
  2 names the same two verbs, so the entry path and the front page agree that
  the model announces the command and the member runs it.
- **`scaffold-init.py check` counts the two kinds it looks at separately.** It
  printed one tally, "29 generated file(s) still match the hash in their
  header", and three of those twenty-nine were host links, which carry no
  header and have no content to hash. The line now reads 26 generated files
  matched and 3 host links in place, `doctor --json` writes the same two
  numbers out of the same function, and `apply` names the kind it wrote each
  link as. Two numbers in a product that mean the same thing and disagree read
  to a member as the tool being broken.
- **The protected-path guard is registered on the shell tool kind as well as
  on the file-writing tools.** Reading a shell write shape was already in the
  guard and nothing routed a shell command to it, so every rule it enforces
  was one heredoc away from being decoration. `hooks-rules.json` now lists
  `shell` beside `file_write` on that rule, and the reader tracks `cd` inside
  the command so a relative path is resolved against the directory in force at
  that point rather than against the session root. An interpreter handed its
  program inline or on stdin (`python3 -c`, `node -e`, a heredoc) is treated
  as unresolvable rather than as non-writing: the call is allowed, one line on
  stderr says the program body was not read, and any protected path spelled
  out literally in that body is still refused. On the shell the unlock is per
  call, an `ICOR_UNLOCK_WRITES=1` prefix on that one command, logged.
- **`run-red-tests.py --fast`.** Three groups do heavy filesystem work and
  dominate the runtime: the manifest guards, which each clone the repo for its
  tag history, the release-residue gate, and the generator end-to-end cases,
  which each build a fixture vault. `--fast` skips those three by name, on
  stdout and in the summary, and changes nothing else: every other guard still
  runs and a failure still exits 1. It exists because `doctor` runs this suite
  on its way to a health report, and a health check nobody waits for is a
  health check nobody runs. A fast run is never reported as a green for the
  groups it skipped, and a case gated on a deliberately broken guard proves a
  fast run still goes red. The release gate and the CI workflow call the file
  with no arguments and get the whole suite.
- **`scaffold-init.py doctor` reads Codex's own config and says whether this
  folder's hooks are trusted**, in words, naming the absolute path it looked
  for. It reports `yes`, `NOT TRUSTED` or unknown, never no on an unreadable
  file, because telling somebody their guards are off because a file could not
  be opened sends them to fix something that may not be broken. It carries
  Codex's sandbox note in the same block: `workspace-write` refuses writes
  into `.codex/` and `.agents/`, so `apply` has to be run by the member from
  their own terminal and not by a model inside a Codex session.

### Fixed

- **`write-guard.py` could not see the path Codex was about to write, so the
  protected-path rule was inert on that host.** Codex's only file-writing tool
  is `apply_patch`, and its payload carries no `file_path`: the paths are
  headers inside the patch body. The guard read two keys and skipped the rule
  in silence, while `hook: PreToolUse Completed` and `doctor` both reported it
  as installed. In the red run the protected daily note and root `AGENTS.md`
  were actually modified. The guard now reads every path out of an
  `apply_patch` body (`Add`, `Update`, `Delete File:` and `Move to:`) and out
  of the shell write shapes (`cat >`, `tee`, `sed -i`, a bare redirect, `mv`
  and `cp` into a path), and resolves a relative path against the working
  directory in force at that point in the command rather than against its own.
  Both shapes were re-run on the fixed build and both are refused verbatim,
  with the file byte-identical afterwards.
- **The contract unlock could not be used on the write it exists for.**
  `ICOR_UNLOCK_WRITES=1` is an environment variable, so a model told to
  "re-run the command with it set" writes the contract from a shell, which is
  exactly where a hook registered on the file tools cannot look. Both pilot
  CLIs did that. The hire path now uses a marker instead: `new-agent.py`
  writes `06 AI Team/Agents/<Name>/.hiring`, `write-guard.py` stands down on
  THAT contract and no other while the marker is younger than 24 hours, and a
  green `check-hire.py <Name>` deletes it. The marker is itself a protected
  path, because a marker planted by any tool would open that contract for a
  day. A marker left behind past 24 hours is a WARN on the new check 23. The
  environment variable remains the second unlock, for an approved edit to
  something that already exists.
- **A Codex session could not tell a member its guards were off.** The `doctor`
  trust line and the warning block in `.codex/config.toml` are both read by
  the member and neither by the model, so across four hooks-off runs a
  scripted Codex session reported a clean pass with nothing behind it. The
  session start ritual already knew: it had to mint its own session id
  precisely because no hook payload arrived. That fact now prints as one line
  naming that the ritual ran by hand, that on Codex it means the project hooks
  are untrusted and every guard is off for this session, and what to run.
- **`scaffold-init.py apply` said INCOMPLETE and exited 0.** A host sandbox
  refused a path, the message said so in prose, and the process still returned
  success, so a model reading the exit code rather than the paragraph reported
  a clean activation with no shims, no skills and no guards behind it. It now
  exits non-zero whenever a path was refused. A script that says INCOMPLETE
  and exits 0 is a green that is not green.
- **`scaffold-init.py apply` crashed instead of explaining when a host sandbox
  refused a write.** Codex's `workspace-write` sandbox refuses `.codex/` and
  `.agents/` even inside the workspace, so the harness came out incomplete
  with nothing said. Refused paths are now named, the run says the harness is
  incomplete, and it prints the command to run from the member's own terminal.
- **`stamp-processed.py` refused the note shape the Scaffold ships.** The
  daily note is blank by design and the script exited 1 with "note has no
  frontmatter block", so the last step of `SOP-1001` was unreachable on a real
  member's note. On Codex that dead end is what sent the model past the script
  and onto the protected path with `apply_patch`. It now creates the block,
  carrying only what GL-1002 requires for the type, and never touches the body.
- **A second stamp no longer leaves two `processed` keys.** A note carrying
  `processed: false` got a second key appended; YAML takes the last one, so it
  worked by luck and read as a corrupt block in the Properties panel. The
  stamp is now replaced, not appended.
- **`SOP-1001` step 1 named a path `validate-scaffold.py` refuses.** It said
  `00 Daily Scratchpad/YYYY-MM-DD.md`; GL-1004, `.obsidian/daily-notes.json`
  and the validator all say `YYYY/MM/`. Following the SOP walked its reader
  into a red gate. Every scratchpad path named in Team Knowledge is now
  checked against that rule.
- **`/checkpoint` on Claude Code died in 177 ms with 0 turns.** The generated
  skill's prerun used `$CLAUDE_PROJECT_DIR` unbraced. Claude Code SUBSTITUTES
  `${CLAUDE_PROJECT_DIR}` into a skill's markdown; it does not export it, so
  the unbraced form reached the shell, expanded to empty, and Claude Code
  aborted the invocation before the model read step 1. The variable resolves
  in hooks, which is what made the unbraced form look correct. Both skills are
  regenerated; the same command now reaches the model in 12 turns.
- **`run-red-tests.py` died with a traceback in every member vault, and
  `doctor` reported `tested: RED` with a stack trace under it as the member's
  first health check.** The suite read `build-release-zip.sh` unconditionally,
  and the release strips that file on purpose. The release-gate cases now SKIP
  with the reason when the build scripts are absent, and a gate reads the
  residue list out of `build-release-zip.sh` so a fourth stripped file is
  covered on the day it is added.
- **`checkpoint.py`'s date-links line could never say a number.**
  `link-dates-to-daily-notes.py --check --json` printed its JSON object and
  then a human `OK` line on the same stdout, so `json.loads` raised on every
  CLEAN vault and the report said "the linker did not answer" permanently.
  Under `--json` the prose line now goes to stderr, and `checkpoint.py` takes
  the first JSON object out of stdout either way.
- **A scratchpad declaring a type that is not a type left the queue in
  silence.** `type: daily` is not in GL-1002; `check-quality.py` trusted the
  declared value over the room, so the note dropped out of the unprocessed
  queue with `processed: false` still on it and the report read zero enum
  violations, zero invented fields and zero unprocessed scratchpads. A
  declared type outside the guideline is now a named finding listing the
  allowed values, and the room wins over it.
- **The secret guard named the wrong vendor.** An Anthropic key was reported
  as an OpenAI key, because the OpenAI shape matches `sk-ant-...` too. A block
  with the wrong label sends whoever reads it to rotate the wrong credential.
- **`new-task.py` could not write `due`, a field GL-1002 declares on a task.**
  Both pilot CLIs generated the file and then hand-edited the file they had
  just generated, on one host through a shell heredoc no guard then saw.
  `--due` and `--related` are now flags, and a due date that is not ISO is
  refused.
- **A completion receipt could name an output guaranteed to rot.** One pilot
  session listed `.icor-for-life/scripts/session.json` among its outputs; the
  next SessionStart rewrote it, so that receipt could never verify again.
  `--write-receipt` now refuses any output under the machine layer.
- **Nothing pointed a resuming session at the receipt.** Both CLIs rebuilt
  "what did the last session do" out of the session log's prose while the
  machine-readable answer sat unread. The session start ritual now prints one
  line naming the newest receipt, its session and its unresolved count.
- **`check-hire.py` check 5 accepted a drawn placeholder as an avatar.** Both
  pilot models produced one to turn the check green, one of them 1254x1254, so
  "is it a square PNG" was never the question. A file that is tiny, one flat
  colour, or named or flagged as a placeholder now reports WARN naming what is
  still owed, and a WARN is not a pass.
- **The generated `.codex/config.toml` now says what a Codex member cannot
  learn anywhere else**: project hooks run only after they are trusted in an
  interactive session (`/hooks`), `codex exec` never asks and therefore runs
  no guards at all in a fresh vault, the trust record is keyed by the vault's
  absolute path so moving the folder drops it silently, and
  `scaffold-init.py apply` has to be run by the member from their own
  terminal.

### Removed

- `.claude/commands/checkpoint.md` became `.claude/skills/checkpoint/SKILL.md`, and the skill runs the script before the model reads step 1

  A skill wins the name `/checkpoint` over a command of the same name, so the
  two could not both stand. Nothing else was removed in this version.

### Known limits

- **`.agents/skills/` is not shipped and not tracked.** `.claude/`, `.codex/`,
  `.gemini/` and `GEMINI.md` are real generated files and ship with the
  scaffold, because they are rendered from tracked frontmatter and carry a
  hash of their source. `.agents/skills/<name>` is different: it is a link
  into `06 AI Team/AI Team Knowledge/Skills/`, and where the platform has no
  symlinks the generator writes a copy instead, so the kind is decided per
  device at write time. Two things follow and both are true today: the
  manifest describes a file by its content hash and a link has none, and
  `build-release-zip.sh` lists the staged tree with `find . -type f`, which
  never matches a link. Codex, Gemini CLI and Cursor users run
  `scaffold-init.py apply` once after copying the vault and the links appear;
  the Claude Code skills under `.claude/skills/` are real files and are
  already there.
- **A hook is not an enforcement boundary.** `write-guard.py` sees the
  file-writing tools, `apply_patch`, and the shell write shapes its reader
  lists. It does not see a program that builds its path from a variable, a
  script already on disk, an interpreter handed its program on stdin (that
  call is allowed with a line saying the body was not read), another process,
  a person, or any host without hooks. The unlock is one environment variable
  or one command prefix away by design. It raises the cost of an accident and
  teaches the right path in the refusal; it is not a permission system.
- **Gemini CLI gets no hooks**, because it has none. Its agents are generated;
  its guards are not, and a Gemini session runs unguarded.
- **`project_doc_max_bytes` in a project-local `.codex/config.toml` is
  unverified.** Whether Codex honours the key outside `~/.codex/config.toml`
  is not something we have watched work, `scaffold-init.py doctor` reports it
  as unverified on every run, and the documented path is to set the same line
  in the home config.
- **Nothing here proves a host reads any of it.** `scaffold-init.py check`
  proves the generated bytes are the bytes the sources produce. That a hook
  fires, a skill gets selected or a shim is picked up is a different claim,
  and it is the one `doctor` reports per host rather than asserts.

## 1.22.0 — 2026-09-13

- Added `06 AI Team/Expansions/` as the home for optional AI Team packs.
  This is an additive myPKA layer, not a replacement architecture or the
  retired top-level runtime expansion system.
- Added `GL-1012-ai-team-expansions` and
  `WS-1006-install-an-ai-team-expansion` for discovery, review, installation,
  activation, updates and removal. Root session discovery now checks packs.
- Added `expansion-pack.py`: hash-checked, additive file installation and
  removal that refuses changed owned files; no lifecycle hooks execute.
- No core agents, personal knowledge, credentials or existing files are
  replaced by a pack. Existing members add the new folder and scripts and
  merge the new discovery step into their root contract, preserving custom
  instructions. No existing folder is moved or removed.

## 1.21.0 — 2026-09-13

- Added root `AGENTS.md` as the single runtime-independent operating contract.
  The substantive instructions previously in `CLAUDE.md` now live here.
- Changed `CLAUDE.md` into an `@AGENTS.md` import with an explicit-read
  fallback; added root `AGENT.md` as a compatibility pointer. Specialist
  `AGENT.md` contracts keep their existing filenames and identities.
- Added `ADAPTER-PROMPT.md` for explicit initialization in runtimes without
  automatic instruction discovery. It preserves existing files and reports
  actual capabilities instead of inventing runtime configuration.
- Updated onboarding and active rule references to the shared contract;
  documented manual checkpoint invocation outside slash-command runtimes.
- Added validation and negative fixtures for the root-entry chain.
- Updating an existing vault: compare your customized `CLAUDE.md` with the
  new `AGENTS.md`, carry your changes into the shared contract, then install
  the thin adapters. Back up and review first; do not overwrite a customized
  contract with the default or run a generic initializer over it.
- No files removed. No personal data or runtime credentials are bundled.

## 1.20.0

Released 2026-09-11.

A date you write is a link to that day. Empty daily notes stop being empty:
they fill up from the outside, by backlink, from every note that mentions
the day. **The daily note is a timeline of YOUR life and work, so only your
own notes link into it:** `04 Inner World/`, `03 WiP/` and `01 Inbox/` are
in scope and all of `06 AI Team/` is out, so a day never fills up with the
team's own housekeeping.

Minor bump: one new Guideline, two new scripts, one new checkpoint flag and
half a validator check, plus the two config fixes below. No file is removed
or moved.

### Added

- **`GL-1011` Date mentions link to daily notes.** A full date written in a
  note body is `[[YYYY-MM-DD]]` and resolves to that day's daily note; the
  daily note is created blank if it is missing. The value is the backlink
  pane: a daily note with nothing in it still shows the journal entry, the
  meeting, the contact and the brief that named that day, assembled by the
  vault rather than by you. Scope is one principle, stated first: only the
  user's own rooms link in, because a session log or a specialist journal
  is how the AI team remembers its own work, and a day buried under the
  team's housekeeping shows you nothing. Inside those rooms the rule is
  narrow for a second reason: a lived-in vault holds around 114k
  `YYYY-MM-DD` strings and almost none of them are prose. Frontmatter dates
  stay bare and that is stated plainly: a typed date there is data that
  Bases and every script read, and a wikilink in a date field is a broken
  value.
- **`Scripts/link-dates-to-daily-notes.py`**, which enforces it
  (`--check`, `--dry-run`, `--fix`, `--since`, `--json`). It reads the
  folder and the format from `.obsidian/daily-notes.json` rather than
  assuming a room, refuses `--fix` when that file is absent, and refuses
  outright when the format's last segment is not `YYYY-MM-DD`, because a
  `[[YYYY-MM-DD]]` link could not resolve to a note named anything else.
  All of `06 AI Team/` is out of scope, and inside the three user rooms so
  are frontmatter, code fences, inline code, existing wikilinks, link
  targets, URLs, slugs, ids, ISO timestamps, filenames, archives and
  templates. A date whose name is taken by some other note is
  reported as a collision and left alone rather than linked into ambiguity.
  Idempotent: a second `--fix` changes nothing.
- **`Scripts/test-link-dates-to-daily-notes.py`**, 27 cases over a fixture
  vault, one per rule the script claims, where every IGNORE case is a date
  it must not touch. `--break-me` flips one expectation so the suite itself
  can be watched going red. `run-red-tests.py` runs the whole suite plus the
  two refusals a member's vault can actually hit.
- **`checkpoint.py --assert-dates-linked`**, and a `date links` row in the
  report. The count is asked of `link-dates-to-daily-notes.py --check`
  rather than re-implemented, so GL-1011's scope has one home; a count it
  could not read prints as `unknown`, never as `0`.
- **`validate-scaffold.py` check 11 now also reads `folder` and `format`**
  from `.obsidian/daily-notes.json` and requires the two values `GL-1004`
  names.

### Fixed

- **The shipped `.obsidian/daily-notes.json` said `format: YYYY-MM-DD`**,
  so Obsidian wrote daily notes flat into `00 Daily Scratchpad/` while
  `GL-1004` said `YYYY/MM/YYYY-MM-DD` and `validate-scaffold.py` check 3
  required the nesting. Nothing read the setting, so the contradiction
  survived every release. Found by the new linker, which reads the format
  instead of assuming it, then created a note the validator rejected. The
  new half of check 11 is the guard that keeps it from coming back.
- **Updating in place with daily notes already written flat**
  (`00 Daily Scratchpad/2026-09-10.md`): nothing moves them. Take the new
  `.obsidian/daily-notes.json` (or set Settings > Daily notes > Date format
  to `YYYY/MM/YYYY-MM-DD`, a preset in the dropdown). From then on Obsidian
  opens and creates `00 Daily Scratchpad/YYYY/MM/YYYY-MM-DD.md` and builds
  the folders itself, but its previous and next commands no longer see the
  flat notes, and a `[[YYYY-MM-DD]]` link for one of those days resolves to
  the flat note, so the linker reports the day as a collision and leaves it
  bare. Move each flat note into its `YYYY/MM/` folder in Obsidian or
  Finder; links use the basename, so nothing inside them changes, and the
  next `--fix` links those days. If you opened today's note before
  switching, you now have two: paste the flat one's text into the nested one
  and delete the flat one.
- **`.gitignore` ignored daily notes only in the flat shape** it no longer
  uses (`00 Daily Scratchpad/2026-*.md`), so a nested daily note was
  trackable and could have shipped in the zip. Personal data must never
  reach a release. The nested shape is now ignored too.

### Changed

- **`WS-1005` gains step 4**, the date-link pass, before the session log is
  written, so the log's own dates are linked; its final assertion is now
  `checkpoint.py --assert-logged --assert-dates-linked`.
- **`GL-1007`** gains one line under "The daily note is blank", pointing at
  `GL-1011`: the note stays blank, and it fills up from the outside.

## 1.19.2

Released 2026-09-11.

### Fixed

- **`build-scaffold-manifest.py` could write a manifest that was stale the
  moment it was committed, and say OK while doing it.** Build the manifest
  while HEAD still carries the PREVIOUS version's tag, which is what happens
  if you bump `VERSION` and build before committing, and the history gets no
  entry for the version being released. `--check` then passes on the machine
  that wrote it and fails in CI on a clean checkout of the tag, which is the
  worst shape a gate can have.

  It now refuses, and prints the order that works: commit first, build with
  HEAD untagged, amend, then tag. Watched going red on a bumped `VERSION`
  over a tagged HEAD, and green on an untagged HEAD with a bumped `VERSION`
  (whose history then carries its own version) and on a clean checkout of a
  tag. The existing "bump VERSION" guard is unchanged and still fires.

  Found the hard way: it cost the 1.19.1 release a failed run.

## 1.19.1

Released 2026-09-11.

### Fixed

- **`GL-1004` described canvas names more narrowly than the check accepts.**
  The naming table said a canvas is `YYYY-MM-DD_canvas.canvas` with `-N` on
  same-day collisions, which reads as if a canvas you have titled yourself is
  wrong. `validate-scaffold.py` accepts a title or a number after `_canvas`
  and always did, so the table now says so. No file moves and no rule
  changes; the page now matches the guard.

## 1.19.0

Released 2026-09-11.

Capture becomes a thing you can be taught. `GL-1010` answers which of the
five ICOR note-taking workflows you are doing, which key you press and why
the vault ships the plugin that makes it work, with a diagram per workflow.
`GL-1007` now states the rule in the order ICOR states it: ask what this
connects to, before you ask where it goes. The Scratchpad ships, so quick
capture works from any app. The Meeting Recorder is cancelled: you bring
your own transcriber and the Scaffold owns the digest.

### Added

- **`GL-1010` The five capture workflows.** One page that answers "which of
  the five ways of taking a note am I doing, which key do I press, and why
  does this vault ship the plugin that makes it work". Eight Mermaid
  diagrams, a step-by-step for each workflow, the key table, and an honest
  shipping-status column: Canvases, PDF Annotation, Outliner, Planner and
  Scaffold Check ship today; Scratchpad and Handwriting are built and not
  yet released. Workflow 4 has no plugin by design, see Removed. Every
  diagram was rendered through mermaid-cli before shipping rather than
  assumed to parse.
- **`note_type: idea`**, the sixth note kind, with `idea_status`
  (`open` / `promoted` / `parked` / `dropped`) and a template. A Topic is a
  quarterly exploration and you run three; a Project is bounded work with a
  finish line. A video idea is neither, and was previously filed as an
  `outline`, which worked and told you nothing about whether the idea was
  still alive. `dropped` with the reason is the valuable state: it stops you
  having the same idea again next year.
- **Three named views on `Notes.base`**: Sources (every `reference`),
  Reading queue (unconsumed sources only) and Open ideas. `new-base.py`
  grew an `extra_views` key to declare them, because a second KIND inside
  one type is a view, never a second Base and never a second folder.
- **Three hotkeys** for the shipped plugins: `Cmd+Alt+H` highlight a PDF
  selection, `Cmd+Alt+L` the highlights sidebar, `Cmd+Alt+D` the canvas pen.
  Only command ids verified in the plugins' own source were bound, because a
  hotkey pointing at an id that does not exist is silently inert.

### Removed

- **The Scratchpad plugin ships from its own release, not from this repo's
  tree.** These three paths were briefly tracked here and are now gitignored
  like every other release-staged plugin:

  - `.obsidian/plugins/icor-for-life-scratchpad/main.js` now comes from the plugin's own `0.1.0` release asset, not from this repo
  - `.obsidian/plugins/icor-for-life-scratchpad/manifest.json` now comes from the plugin's own `0.1.0` release asset, not from this repo
  - `.obsidian/plugins/icor-for-life-scratchpad/styles.css` now comes from the plugin's own `0.1.0` release asset, not from this repo

  Nothing is lost: the release zip stages all three from the plugin's own
  published `0.1.0` release, with its build-provenance attestation, which is
  the certified artifact by construction. This is the same path `chat`,
  `terminal` and `canvases` already take, and it is the right one for any
  plugin whose `main.js` is a build output its own repo does not track. If
  you have these files in your vault, keep them: they are the plugin, and
  the download puts them back.

- **The Meeting Recorder is cancelled and the Scaffold will not record
  meetings** (Tom, 2026-09-11). You already have a transcriber you trust,
  or your company does: Wispr Flow, Granola, Otter, Fireflies, the one in
  your call software. Building a worse one inside Obsidian would have been
  a second-rate copy of a solved problem and would have tied your meeting
  notes to our plugin. What the Scaffold owns is the part no transcriber
  does: turning an hour of what was said into the few lines of what you now
  think.

  What this changed. `GL-1002` §"Meeting recordings: the four recording
  fields" is now §"Meeting notes: bring your own transcriber". The
  `recording` field (a wikilink into a package) becomes `transcript`, which
  holds a URL to your tool, a wikilink to an exported file, or a wikilink
  to a transcript note, whichever is true for you. `transcribed_by` now
  holds the tool's name in the words you would say out loud (`Wispr Flow`),
  not an engine and model id. `audio_retained` now means "can I still
  re-listen to this", which is a question the note cannot otherwise answer.
  `SOP-1015 Process a meeting recording` is now `SOP-1015 Digest a meeting
  transcript`, tool-agnostic, taking a transcript and a steer and returning
  note content. `05 Assets/Recordings/` is gone; exported audio, if you keep
  any, goes in `05 Assets/Audio/`. `GL-1001` and `GL-1008` no longer
  describe a package.

  **Consent moved with it.** The Scaffold never starts a recording, so it
  never asks for consent on your behalf. Whatever your transcriber asks,
  and whatever the law where you and the other people are, is between you
  and the room.

### Changed

- **`GL-1007` now states the capture rule in the order ICOR states it:
  ask what this connects to, before you ask where it goes.** The page
  previously carried only the negative half ("at capture time you never
  choose a destination") and omitted the positive half, so captures landed
  fast and landed unfindable. One link is now the price of closing a
  capture, and orphan captures are named as the thing to let go.
- **`GL-1007`: direct placement is normal, the door is the fallback.** The
  page opened with an absolute that contradicted ICOR's own inbox doctrine
  ("the inbox is your backup plan, not your primary strategy"). A phone
  number goes on the person's note; `Cmd+O` is the key. The five-minute rule
  is stated as the health check.
- **`GL-1007` says where outer material actually lives.**
  `01 Inbox/Outer World/` is named for what ARRIVES there, not for where
  outer material stays, and the asymmetry with the permanent `04 Inner
  World/` room is what confuses people. Outer material lives in
  `04 Inner World/Notes/` as `note_type: reference` with its `source_url`;
  the outer-world library is the Sources view, not a room. The folder was
  deliberately NOT renamed: the Web Clipper template writes to that path in
  every installed vault, and breaking workflow 5 everywhere to improve a
  name is a bad trade.

- **`GL-1004` now rules that the Daily Scratchpad is date-nested, exactly like
  the Journal.** Everything lands in `00 Daily Scratchpad/YYYY/MM/`, and the
  quick capture is named `YYYYMMDDHHmm.md` (optionally ` - Title` added after
  the fact), not `YYYY-MM-DD-HHmmss.md`. This is the shape the Scaffold's own
  two settings already produce: `.obsidian/daily-notes.json` writes
  `YYYY/MM/YYYY-MM-DD` and the ICOR for Life - Scratchpad plugin writes
  `YYYYMMDDHHmm` into `YYYY/MM`. The guideline described a vault nobody was
  running, so the guideline moved.

### Fixed

- **`Scripts/validate-scaffold.py` could not enforce the scratchpad rule it
  claimed to enforce.** It globbed the room ROOT (`sp.glob("*.md")`), so the
  moment a vault nested its scratchpads the check matched zero files and
  passed by finding nothing. It walks the whole room now and asserts the
  `YYYY/MM/` nesting as well as the name. Watched going red on a file loose at
  the root, a file nested only by year, and a title-named note, and green on
  the daily note, the quick capture, a titled quick capture and both canvas
  shapes.

## 1.18.0

Released 2026-09-09.

Filing by hand works out of the box. The Scaffold now ships the ten note
templates, the property types and the hotkeys that let Obsidian's own
Templates and Properties panels file a note the way `GL-1002` describes it,
and `GL-1007` walks through every step without the AI. The team knows the
same moves: Penn checks and repairs what you filed by hand, and only with
your yes (`SOP-1014`). A new script, `Scripts/check-quality.py`, measures
thirteen quality metrics over your knowledge and writes them to the machine
layer, where ICOR for Life - Scaffold Check 0.4.0 shows them in its report
and on a dashboard.

**Updating from 1.17.0.** The moment this version is published, your next
Scaffold Check lists the new files below (the templates, the three scripts,
`GL-1008`, `SOP-1014`, the SOPs index, `.obsidian/templates.json`,
`.obsidian/types.json`, `.obsidian/hotkeys.json`) as missing, at attention
severity. That is the normal update signal, not a defect: download 1.18.0,
copy the files in, and the list empties. No file is removed or moved in this
version.

### Added: the machine layer, `GL-1008`

`.icor-for-life/` is now the suite's machine layer: the one hidden folder
every ICOR for Life plugin and every vault script uses for data that another
plugin or script reads. The four scaffold files stay as they are; a plugin
writes under `.icor-for-life/<plugin-id>/` (the id exactly as in its
`manifest.json`) and the vault's scripts write under `.icor-for-life/scripts/`
(first file: `quality.json`, written by the quality script, read by Scaffold
Check, shape versioned by a top-level `schema` integer). A file belongs there
only if something regenerates it: never a source, never a user setting (those
stay in `.obsidian/plugins/<id>/data.json`), never anything a person reads
(Obsidian does not show, index or search a dot folder; a human report stays a
note in a room). Plugins reach it through `app.vault.adapter` only, on desktop
and on mobile alike, and create their own subfolder on first write. Obsidian
Sync does not carry the folder, so it is per device and rebuildable. The rule
is `06 AI Team/AI Team Knowledge/Guidelines/GL-1008-the-machine-layer.md`;
`.icor-for-life/README.md` shows the layout; `.gitignore` now ignores the
folder except `VERSION`, `manifest.json`, `CHANGELOG.md` and `README.md`.

No file is removed or moved.

### Changed: the team checks and repairs what you filed by hand

The member may do every filing step by hand
([[GL-1007-capture-and-where-things-go|GL-1007]], "Doing it by hand, step by step"); the
team now knows it, does the same steps on request, and checks and repairs
the result with the member's yes, never silently.

- `06 AI Team/Agents/Penn/AGENT.md`, `06 AI Team/Agents/Penn/Penn.md`: Penn's mission widens to keeping what the user filed by hand correct and connected; Penn owns SOP-1014, runs every entity through `find-entity.py` and `new-entity.py`, never applies a repair to a user-made note without a yes and never deletes one. New trigger phrases: "check my notes", "did I file that right", "fix my vault".
- `06 AI Team/Agents/Silas/AGENT.md`, `06 AI Team/Agents/Silas/Silas.md`: the audit duty runs `validate-scaffold.py`, `check-bases.py` and `check-quality.py` at session start via Larry, on request and after every import; structural repairs (a base, a folder, a script) are Silas's, content repairs go to Penn via SOP-1014.
- `06 AI Team/Agents/Larry/AGENT.md`, `06 AI Team/Agents/Larry/Larry.md`: Larry owns vault health: reads `.icor-for-life/scripts/quality.json` at session start (runs `check-quality.py --write` first if it is missing or older than today), reports it in one line, routes `attention` or `broken` to Penn with the user's yes.
- `CLAUDE.md`: the session start ritual gains the vault health step (new step 3, after the Tasks walk, before the Inbox check); the mermaid authoring pointer now names `06 AI Team/README.md` (the old path `06 AI Team/AI Team Knowledge/README.md` never existed); hard rule 5 points at GL-1004 for folders instead of restating it.
- `06 AI Team/AI Team Knowledge/Workstreams/WS-1003-onboarding-first-launch.md`: the tour opens GL-1007 right after the Notes stop, the two-door sentence ends with both doors to filing ("you can file it yourself from there, or the team does it for you"), the templates are named as the pasteable shape and the examples may go once real content exists, and the close names the Scaffold Check plugin as the vault health readout.
- `06 AI Team/Agents/agent-index.md`: Penn's and Silas's rows updated to match.

### Changed: filing by hand is a first-class path (Penn)

Knowledge management, note organization, links and properties can all be
done by hand, without the AI, and the team knows those same moves so it
can do them for you or repair them afterwards.

- `GL-1007` gains "Doing it by hand, step by step": the one walkthrough
  (right-click the room, New note; Templates: Insert template; the
  Properties panel and the `[[` move for a wikilink in a list; the link
  rule; the month folder for a journal entry; a file on the shelf and its
  `document` wrapper; the processed stamp by hand; where the Scaffold
  Check report lands). Every other surface links there.
- `GL-1002`: a `template` column per type (`[[Templates/<type>]]`, the
  template is the SSOT for the YAML), the Properties UI sentence once in
  the common section, and the processed stamp may now be typed by hand in
  the one shape the script writes; `check-quality.py` verifies the shape
  either way.
- `GL-1004`: who creates a folder. Rooms and fixed subfolders are the
  Scaffold's; `YYYY/MM/` date folders may be made by hand or by script;
  anything else asks the AI first.
- `SOP-1001`, `SOP-1002`: open with the by-hand sentence and every
  `[SCRIPT]` step names its by-hand twin. `SOP-1004`, `SOP-1005`: the
  duplicate check is `Scripts/find-entity.py`, creation is
  `Scripts/new-entity.py`.
- New `SOP-1014-check-and-repair-what-was-filed-by-hand` (Penn): reads
  `quality.json`, proposes deterministic repairs for a yes, asks the
  judgement ones as one-line questions, hands `unprocessed_*` to
  SOP-1001 / SOP-1002, never rewrites, never deletes.
- `WS-1001` step 4 runs the quality check after the two doors;
  `WS-1002` step 4 runs it over `04 Inner World` and asks the read-later
  backlog as the weekly question.
- Added `06 AI Team/AI Team Knowledge/SOPs/INDEX.md` (every SOP, owner,
  trigger) and `04 Inner World/Contacts/README.md` (the one room README
  that was missing).
- `README.md` first steps: step 3 has its no-AI alternative, new step 4
  "File your first note by hand". `04 Inner World/README.md` no longer
  says only the AI files there.

### Added: the templates, the property types, and a quality check (Mack)

Filing by hand now has real machinery behind it, and the vault can measure
what came out.

- Ten templates in `06 AI Team/AI Team Knowledge/Templates/`
  (`journal`, `note`, `document`, `person`, `company`, `project`, `goal`,
  `habit`, `topic`, `key-element`), each carrying exactly the fields
  GL-1002 declares for its type, required first, with `{{title}}` and
  `{{date}}` filled by the core Templates plugin.
  `.obsidian/templates.json` points at that folder and pins
  `dateFormat` to `YYYY-MM-DD`, so **Templates: Insert template** works
  from the first launch and `created` arrives date-typed.
- `.obsidian/types.json` declares all 107 property names GL-1002 uses,
  with the right Obsidian type. Every wikilink list is `multitext`, so
  the Properties panel offers the `[[` suggestion and Bases reads two
  values where there are two. `tags` and `aliases` carry Obsidian's own
  names, because its MetadataTypeManager owns those two and rewrites any
  other value on the first type change in the vault.
- `.obsidian/hotkeys.json`: Insert template, Create new unique note, Open
  today's daily note and Show file properties on `Cmd/Ctrl+Alt` `T`, `N`,
  `S` and `P`. (`S` for Scratchpad: `Cmd+Alt+D` toggles the macOS Dock.)
- `06 AI Team/AI Team Knowledge/Scripts/new-entity.py`: creates one entity
  note from its template, in its room, already linked, and refuses an
  unknown type, a title GL-1004 forbids, an existing note, a link to
  nothing, a `note` filed under nothing, a project with no goal, an
  invented field and a value outside a GL-1002 value set.
- `06 AI Team/AI Team Knowledge/Scripts/find-entity.py`: the duplicate
  check before anything is created, by filename, `name`, `title` or an
  alias. JSON out, exit 2 when there is no hit.
- `06 AI Team/AI Team Knowledge/Scripts/check-quality.py`: thirteen
  metrics over `04 Inner World/`, `00 Daily Scratchpad/` and `01 Inbox/`
  with one `health` verdict, and `--write` for
  `.icor-for-life/scripts/quality.json` (schema 1), which the ICOR for
  Life - Scaffold Check plugin reads and shows as a dashboard. The field
  list is documented in the new
  `06 AI Team/AI Team Knowledge/Scripts/README.md`.
- `validate-scaffold.py` gains check 12 (templates.json points at the
  Templates folder, every template declares a GL-1002 type, every
  template GL-1002 names exists) and check 13 (every list property is
  `multitext` in types.json, with the three reserved names Obsidian owns
  held to Obsidian's values instead). `run-red-tests.py` covers all of
  it: 100 guards now, up from 76.
- `new-base.py` reads GL-1002's per-type table BY HEADER NAME instead of
  by column position, and exposes `gl002_required()` and `gl002_enums()`
  beside `gl002_fields()` so no other script re-parses the guideline.
  **Fixed:** the new `template` column had shifted the positional parse,
  and `check-bases.py` was reporting all four shipped `.base` files as
  carrying columns GL-1002 does not declare.
- One example note, `04 Inner World/Notes/Why I keep a Daily Scratchpad.md`,
  so `Notes.base` shows a row on first launch.

No file is removed or moved.

### Changed: Scaffold Check 0.4.0 inside

ICOR for Life - Scaffold Check 0.4.0 inside: the report gains a "Knowledge
quality" section and a new dashboard view with a trend line per metric, both
read from `.icor-for-life/scripts/quality.json` as written by
`Scripts/check-quality.py --write`. The plugin never measures; it shows what
the script wrote. Without the file it says in one sentence how to get one; a
file with another schema, or numbers older than seven days, is named as such
and never stops a check. The plugin's run history lives at
`.icor-for-life/icor-for-life-scaffold-check/history.json`, per device,
capped at ninety runs, following `GL-1008`.

Minor bump: one new Guideline, one new SOP, ten templates, three new scripts,
two new validator checks, three new `.obsidian` settings files, one example
note, and one bundled plugin feature.

No file is removed or moved.

## 1.17.0

Released 2026-09-09.

### Changed: `04 Inner World/Documents` is now `04 Inner World/Notes`

The room for a note that lives on. ICOR has one atomic unit, the Note, and
the scaffold had no home for one: an outline you keep editing, a reference
you saved, notes from a meeting, a draft on its way somewhere else. The
`Documents` folder held only file wrappers (`type: document`, a binary
behind every note) and became the catch-all for everything else. It is
renamed to `Notes` and holds two types side by side: `type: note` (new) and
`type: document` (unchanged: a document is a note with a file attached, not
a second kind of thing). `05 Assets/Documents/`, the shelf for the binaries
themselves, keeps its name.

**Updating by hand: rename the folder, do not create a second one.**
Scaffold Check on 1.17.0 reports "Required folder is missing:
`04 Inner World/Notes`" until the folder exists; the fix is to rename your
`04 Inner World/Documents` to `04 Inner World/Notes` in Obsidian's file tree
(Obsidian rewrites every wikilink for you), then replace the four files
below. Creating a new empty `Notes` folder next to the old one leaves you
with both, your wrapper notes in the wrong place, and `Documents.base`
pointing at a folder the scaffold no longer describes.

Every moved file, and where it went:

- `04 Inner World/Documents/README.md`: rewritten and moved to `04 Inner World/Notes/README.md` (git sees a delete and an add because the text changed as well as the path)
- `04 Inner World/Documents/Documents.base`: moved to `04 Inner World/Notes/Documents.base` (its folder filter now reads `04 Inner World/Notes`; still the `type == document` view)
- `04 Inner World/Documents/Example Invoice.md`: moved to `04 Inner World/Notes/Example Invoice.md`
- `04 Inner World/Documents/Highlights/.gitkeep`: moved to `04 Inner World/Notes/Highlights/.gitkeep` (the PDF Annotation plugin's default highlights folder moves with it, see below)

### Added: the note schema, the capture guide, a Web Clipper template

- `04 Inner World/Notes/Notes.base`: the `type == note` view (Kind,
  Projects, Key Elements, Topics, Source, Consumed). It sits next to
  `Documents.base` in the same folder; one folder, two collections split by
  type.
- `06 AI Team/AI Team Knowledge/Guidelines/GL-1007-capture-and-where-things-go.md`:
  the capture guide in ICOR's words. Two doors (`00 Daily Scratchpad` for
  what comes out of you, `01 Inbox/Outer World` for what someone else
  made), the Capturing Beast filter (Project, Key Element, Topic), then one
  home per kind of note. `README.md` "First steps" gains step 4 and links
  it; `WS-1003` adds the Notes README as a tour stop and says the two-door
  sentence; `GL-1001` rule 1 links it.
- `06 AI Team/AI Team Knowledge/Templates/web-clipper-outer-world.json`: an
  Obsidian Web Clipper template (import under the extension's Settings,
  Templates, Import). It files into `01 Inbox/Outer World` as
  `YYYY-MM-DD-<title>` with `type: capture`, `source_url`, `author`,
  `published`, `captured` and a `my_thought` field you fill in the popup;
  the clipper's default properties (`source`, `created`, `tags: clippings`)
  are not what `SOP-1002` reads.
- `GL-1002`: `type: note` with a required, closed `note_type` (`reference`,
  `outline`, `meeting`, `draft`, `other`) and at least one of `projects`,
  `key_elements`, `topics`; `source_url` and `consumed` on a `reference`;
  the same three link lists as optional fields on `document`; `author`,
  `published` and `my_thought` as optional fields on `capture`. The
  "Documents" section becomes "Notes: notes and the wrapper-note pattern".
- `Scripts/validate-scaffold.py`, two new checks: 10, every `type: note`
  under `04 Inner World/Notes/` carries a `note_type` from the set and at
  least one non-empty link list; 11, `.obsidian/daily-notes.json` carries
  no `template` key, so the daily scratchpad stays blank. The required
  room list reads `04 Inner World/Notes`. `Scripts/run-red-tests.py`
  watches both go red (a note with no kind, a fifth kind, a note filed
  under nothing, a template key with a path and with an empty value) and
  a good note stay green.
- `Scripts/check-bases.py`: a collection is (folder, `note.type`), not the
  folder alone, so `Documents.base` and `Notes.base` may share a folder;
  two bases in one folder that do not both name a distinct type are still
  one collection claimed twice, and the red test covers it.
  `Scripts/new-base.py` gains the `note` entry and the same rule;
  `Scripts/stamp-processed.py` names the new path in its two messages.
- Prose follows the rename in `CLAUDE.md` rule 2, `SOP-1002` step 3 and
  step 5 (a capture without a thought becomes a `reference` note with
  `consumed: false`, linked to its Topic), `SOP-1010` step 1, `GL-1006`,
  `00 Daily Scratchpad/README.md` (no template, no properties),
  `01 Inbox/README.md`, `01 Inbox/Outer World/README.md` and
  `04 Inner World/README.md`.

### Changed: PDF Annotation 0.1.3 inside

ICOR for Life - PDF Annotation 0.1.3 inside: the default highlights folder
follows the rename (`04 Inner World/Notes/Highlights`). An install that
still holds the old default in its settings is moved to the new one on
load; a folder you chose yourself is left as it is. Existing highlight
notes keep working wherever they are.

Minor bump: a room rename with the files above, one new Guideline, one new
Base, one new template, two new validator checks, and one bundled plugin
fix.

## 1.16.0

Released 2026-09-09.

### Changed: AI Chat 0.13.0 inside

ICOR for Life - AI Chat 0.13.0 inside: keys move to Obsidian secret storage.
The own-key engine's Anthropic and OpenRouter keys live in Obsidian's
keychain (Settings, General, Keychain; Obsidian 1.11.4 or newer) under
`icor-for-life-chat-anthropic-api-key` and
`icor-for-life-chat-openrouter-api-key`, or, by choice, in an env file in the
vault (`06 AI Team/AI Team Knowledge/.env` by default, variables
`ANTHROPIC_API_KEY` and `OPENROUTER_API_KEY`). One dropdown picks the place
and the plugin reads that place only; the settings tab says where each key
is and moves it between the two on a button. The paste field is write-only
and empties after Save, and no key is ever shown back. A key left in the
pre-release local-storage record is moved into the keychain on load. This is
the fourth and last plugin of the suite on the "Where your keys live"
setting that 1.15.0 introduced for Connect, Scaffold Check and Planner.

AI Chat's minimum Obsidian version is now 1.8.7 (it was 1.7.2 for 0.12.0 and
0.12.1, which keep that floor in the plugin's `versions.json`). The own-key
engine's per-device settings are kept with `App.loadLocalStorage` and
`App.saveLocalStorage`, both added in Obsidian 1.8.7 and called at load. The
keychain needs 1.11.4; below that the env file is the only backend and the
settings tab says so.

Minor bump: one bundled plugin feature, no scaffold file changes.

No file is removed or moved.

## 1.15.0

Released 2026-09-09.

### Changed: Connect 0.15.0, Scaffold Check 0.3.0 and Planner 0.12.0 inside

Three bundled plugins move on one theme: where a member's keys live. Each
gains a "Where your keys live" setting with two backends, Obsidian's keychain
(Settings, General, Keychain; the default on Obsidian 1.11.4 and newer) or a
`KEY=value` env file inside the vault (`06 AI Team/AI Team Knowledge/.env` by
default, the path is a setting). Only the selected backend is read, there is
no fallback to the other, and the settings tab shows per key where a value
exists with a "Move to ..." button. The env file writer edits exactly its own
lines and leaves every other byte of the file as it was. The keychain is per
device and Obsidian Sync skips files whose name starts with a dot, so a key
set on the desktop reaches a phone through the env file only where the sync
carries hidden files (iCloud Drive, git, Dropbox), or by pasting it again on
that device; each plugin's README says so.

ICOR for Life - Connect 0.15.0 inside: the access token and the refresh token
leave `data.json` for Obsidian secret storage, with the env file as the
option (`MYICOR_ACCESS_TOKEN`, `MYICOR_REFRESH_TOKEN`); a vault that connected
with an older Connect has its keys moved out of `data.json` the first time
this version loads, once, and never back. No key ever appears in a notice or
in the console, not even masked. And the loop percent on the Overview now
matches the app: a member reported 15% in the plugin against 98% on the Your
Loop page, because the plugin computed its own mean of course progress; the
percent and "Courses closed n of m" now come from the server's
`get_my_journey`, fixed on the server and in the plugin.

ICOR for Life - Scaffold Check 0.3.0 inside: the GitHub token leaves
`data.json` for Obsidian secret storage or the env file (`GITHUB_TOKEN`), is
moved into the keychain once on first load, and is entered through a password
field that is cleared once saved. The env file path refuses an absolute path,
a `~` and any `..` segment, and the file is split by a loop that keeps each
line's terminator, so the plugin loads on iOS before 16.4.

ICOR for Life - Planner 0.12.0 inside: the env file as the second place for
the Todoist, ClickUp, IMAP, Outlook and per-calendar keys, Obsidian's keychain
stays the default and unchanged for everyone who already has keys there. The
env file is read again before every sync, so a line edited by hand is picked
up without a restart, and a key is blanked in `data.json` only after its line
is on the env file's disk; a write that fails leaves the key where it was and
the settings tab says so once.

Minor bump: three bundled plugin features, no scaffold file changes. AI Chat
stays at 0.12.1; its next version is not released.

No file is removed or moved.

## 1.14.0

Released 2026-09-07.

### Changed: Planner 0.11.0 inside

ICOR for Life - Planner 0.11.0 inside: dates and times on the board follow
the Date format and Time format from Obsidian's Templates settings, or the
planner's own when that core plugin is off. The habit import keeps the YAML
comment lines of the My Life note, writes `started_on` as the local calendar
date instead of the UTC day, and leaves an absent `month_day` absent instead
of writing the 1st.

Minor bump: a bundled plugin feature, with the four script fixes below.

### Fixed: four defects reported from a live 1.10.2 vault

Reported by community member Andrew Gillley, 2026-09-07, from running the
scaffold's scripts inside his own vault. All four were still present at
1.13.0 and none is specific to his vault.

- `00 Daily Scratchpad/README.md` linked `SOP-1001-process-a-daily-scratchpad`
  and `GL-1004-naming-and-linking`; the files are
  `SOP-1001-process-the-daily-scratchpad` and `GL-1004-naming-rules`. Both
  links fixed; a sweep of every `[[SOP-`, `[[GL-` and `[[WS-` link in the
  download found no other unresolved variant.

- `06 AI Team/AI Team Knowledge/Scripts/checkpoint.py` scanned only
  `Tasks/open/` and `Tasks/in-progress/` for files changed since the last
  session log, so a task closed to `Tasks/done/YYYY/MM/` earlier in the same
  session was invisible and the report printed `tasks touched : 0`. It now
  walks the date-nested `Tasks/done/` and `Tasks/cancelled/` trees as well,
  prints every touched task with its state and path, and the JSON report
  keeps its shape: each entry gains `path`, and a `tasks_touched_by_state`
  count is added; nothing is renamed. Only open and in-progress tasks still
  feed the WiP reference check. `run-red-tests.py` gains
  `checkpoint/done-task-visible`: a done task newer than the last log must
  be listed, a done task older than it must not, watched red against the
  old scan.

- `06 AI Team/AI Team Knowledge/Scripts/validate-scaffold.py` check 6 (every
  folder inside a room gets a colour and a glyph in the file tree) read
  `.obsidian/snippets/icor-rooms.css`, which 1.4.0 retired into the theme,
  behind an `is_file()` guard: in every shipped vault the read was skipped
  and the check passed by covering nothing. It now reads the rules where
  they live: the theme `appearance.json` names first, then any
  `.obsidian/themes/*/theme.css` carrying room rules, then the snippet as a
  fallback; and with none of them present it prints
  `SKIPPED check 6 (file-tree styling): <reason>` and exits 0, never a
  silent pass. The theme's selector grammar (`:is()`, `:not([data-icor-kind])`,
  `:not(:where(...))`, the glyph as `--room-icon`) is evaluated the way CSS
  does instead of by a regex that only knew the snippet's shape, and a
  selector shape it cannot read is a named FAIL, not a dropped rule.
  Confirmed on INKLINE 1.6.0's `theme.css`: the shipped tree passes, an
  unstyled `08` room fails, dated folders are declined by the floor exactly
  as before, and the same rules through the snippet path give the same
  answer. New `--json` flag: `{root, ok, fails, skipped, sources}`, so a
  caller can tell a pass from a skip. `run-red-tests.py` gains four guards
  (an unstyled room under the theme is red by name, the shipped tree under
  the theme is green and names the theme as read, no rule source is
  SKIPPED on stdout and in the JSON, an unreadable selector is red), all
  watched red against the old check.

- `06 AI Team/AI Team Knowledge/Scripts/run-red-tests.py` could not run in a
  member's vault: its manifest guards `git clone` the vault root for the tag
  history, which assumes the scaffold repo, and in a plain folder the run
  died with `CalledProcessError ... exit status 128`. The six manifest guards
  now run only when the root is the top of a git work tree that carries a
  release tag; otherwise each prints `SKIP <guard>: <reason>` and the summary
  counts them (`OK 55/55 guards went red on bad input, 6 skipped (...)`),
  never a silent pass. Exit stays 0 when everything that ran passed. The
  three other fixes in this section add seven guards, so the repo's own run
  reports 62.

No file is removed or moved.

## 1.13.1

Released 2026-09-07.

### Changed: Canvases 0.3.1 inside

ICOR for Life - Canvases 0.3.1 inside: the shapes on text cards are SVG
geometry with no `clip-path`, and the index finds canvas files through
Obsidian's metadata cache instead of enumerating the vault. Both answer
the community directory's scan of 0.3.0.

Patch bump: a bundled plugin update, no tracked vault file changes.

No file is removed or moved.

## 1.13.0

Released 2026-09-07.

### Added: the ICOR for Life - Canvases plugin

**ICOR for Life - Canvases** (`icor-for-life-canvases`, 0.3.0) ships and
is enabled in this download: Obsidian's canvas the way Heptabase does
it. Draw on a canvas with a pen and the ink saves into the .canvas file;
Select, Hand, Pen and Eraser in the canvas's controls column; shapes,
outline, fill and text colours for text cards; canvases inside canvases
with a breadcrumb back up; a zoom bar and a minimap; and under every
note, and in the Backlinks pane, the canvases the note is on and what
its card connects to there. Every key it writes into a .canvas file is
documented in the plugin's `docs/canvas-format.md`; other plugins' keys
are kept.

The plugin joins `community-plugins.json` and the license table in
`LICENSE.md`, under the ICOR for Life Source-Available License (Code)
v1.0; it bundles no third-party code. `README.md` names it among the
first-party suite. The zip builder stages it from the plugin's latest
GitHub release, the way it stages AI Chat and Terminal, and its plugin
inventory names it.

Minor bump: a new plugin out of the box. No tracked vault file changes.

No file is removed or moved.

## 1.12.0

Released 2026-09-07.

### Added: the ICOR for Life - PDF Annotation plugin

**ICOR for Life - PDF Annotation** (`icor-for-life-pdf-annotation`, 0.1.2)
ships and is enabled in this download: highlights on Obsidian's built-in
PDF viewer that are notes in the vault. Select text in a PDF and a toolbar
appears: pick one of six colors, copy a deep link, add a note; hold Cmd
(Ctrl) and drag to highlight an area, saved as a PNG. Every highlight is
one markdown note (`type: pdf-highlight`): position, color and quote in
the frontmatter, your own thoughts under `## Note`. Highlights are painted
back over the PDF, open from a deep link, drag onto a canvas as a card,
and are listed in a sidebar for the open PDF. The PDF itself is never
changed. Desktop and mobile.

`.obsidian/plugins/icor-for-life-pdf-annotation/` (`main.js`,
`manifest.json`, `styles.css`) is tracked the way the Outliner's folder
is, byte-identical to the 0.1.2 release assets. The plugin joins
`community-plugins.json`, the license table in `LICENSE.md` under the
ICOR for Life Source-Available License (Code) v1.0 (it bundles no
third-party code; the `rect=` and `color=` link parameters share the
PDF++ plugin's names, MIT, two names and no code, said so in
`THIRD-PARTY-NOTICES.md`), the suite list in `README.md`, and the zip
builder's plugin inventory. `04 Inner World/Documents/Highlights/` ships
empty as the plugin's default folder (a setting), one subfolder per PDF
once you highlight; `04 Inner World/Documents/README.md` says so.

`GL-1002` gains the `pdf-highlight` type: the field table, the home path,
the body shape (`> quote ^quote`, `![[image]] ^image` for an area
highlight, `## Note`) and two rulings: `canvases` and `linked_notes` are
flat wikilink lists, so a canvas edge is a real edge in the graph and in
Bases; and no `Highlights.base` ships yet, since `Documents.base` filters
on `type: document` and highlights never appear in it.

### Changed: Interface 0.6.5 inside

Interface 0.6.5 inside: the status bar fold button points the way it moves
and hides until the pointer nears it.

### Changed: a plugin folder in the download holds only what Obsidian loads

The zip builder stages each first-party plugin from its repo by path:
`main.js`, `manifest.json`, `styles.css` (the INKLINE theme:
`manifest.json`, `theme.css`) and nothing else. Until now a whole-repo
archive put each plugin's sources, tests, `package.json` and, from
2026-09-07, its own GitHub release workflow into the vault, where the
builder's residue scan rightly refused the workflow. The staged shape is
asserted before the residue scan, no `.github` directory may survive
anywhere in the download, and the builder's self-test can plant the
2026-09-07 shape to watch all three gates go red. The release workflow's
dry run also gains the `main` ref a tag push's detached checkout never
carried, the cause of the 1.11.2 tag's red before any plugin was staged.
The third-party notices for the libraries inside the plugins live in the
root `THIRD-PARTY-NOTICES.md`, as before.

Minor bump: a new plugin and a new note type. The 1.11.2 section that sat
on `main` untagged (the Interface swap) folds in here.

No file is removed or moved.

## 1.11.1

Released 2026-09-07.

### Changed: the manifest lists the shipped agents with their `myicor_id`

`manifest.json` gains a top-level `agents` key: an array sorted by name,
one entry per shipped agent that is not a template, each carrying the
agent's `name` (the folder name), its `myicor_id` read from the contract,
the `path` of the contract and the `shim` (`.claude/agents/<slug>.md`, or
null where none ships). The manifest lists the shipped agents with their
`myicor_id`, so Scaffold Check can recognise a shipped agent by identity
even after a member renames it; a fresh hire is never mistaken for one.
The schema number stays 1: the key is additive, and a checker must accept
a manifest without it.

`06 AI Team/AI Team Knowledge/Scripts/build-scaffold-manifest.py` reads
the id through `mint-agent-ids.py`'s own frontmatter reader, so the UUID
rule keeps one home, and a contract without a valid id fails the build by
name rather than shipping a manifest that is missing an agent. `--check`
names the agents list as its own stale reason. `run-red-tests.py` keeps
two refusals red: a malformed id fails the build and leaves the manifest
untouched, and a changed id makes `--check` go red for the agents list.

Patch bump: the manifest's content changes, no vault file does.

Scaffold Check 0.2.0 inside: it reads the agents list and reports
identity, not just paths.

No file is removed or moved.

## 1.11.0

Released 2026-09-07.

### Added: every agent contract carries a stable `myicor_id`

Every `06 AI Team/Agents/<Name>/AGENT.md` now carries `myicor_id`, a UUID
v4 in lowercase, minted once and never changed, written first after
`type:`. The hiring SOP mints one per hire; the nine shipped agents keep
the same identity across scaffold releases and inside any vault that
carries them. The name, the avatar and the contract text can all change
under a member's hands; the id is the one fact by which a future install
(ICOR for Life - Connect, for agents delivered from the myICOR library)
can tell an agent that is already in the vault from one that is not, and
it is the same UUID the library row for that agent carries as its primary
key. Defined in
`06 AI Team/AI Team Knowledge/Guidelines/GL-1002-frontmatter-conventions.md`
(ruling 2026-09-07, plus the `agent` row of the per-type table);
`SOP-1007` mints it at hire and `SOP-1011` keeps one that arrives with an
imported agent.

`06 AI Team/AI Team Knowledge/Scripts/mint-agent-ids.py` is new: it inserts
the field where it is missing, refuses to change an existing value, prints
the name-to-id map with `--export`, and validates with `--check` (missing,
malformed, shared, or a template off its placeholder).
`validate-scaffold.py` runs that check as its ninth item, watched red on a
contract with the field removed before it went green; `run-red-tests.py`
keeps four of its refusals red, including the refusal to change an id.
`06 AI Team/Agents/Agent 01/AGENT.md` carries the nil placeholder
`00000000-0000-0000-0000-000000000000` that the hiring SOP replaces.

No file is removed or moved.

## 1.10.2

Released 2026-09-06.

### Changed: Connect 0.14.0, the terminal button leaves the right side panel

The top-row terminal button in the right side panel is gone. The terminal is
ICOR for Life - Terminal, launched from its own toolbar entry under the ICOR
for Life logo in the left side panel. The settings gear stays where it was.

## 1.10.1

Released 2026-09-06.

### Changed: the Code license text now says what it always meant, and every plugin gets a CONTRIBUTING.md

A member reading section 2(b) of the ICOR for Life Source-Available
License (Code) v1.0 correctly parsed it as "no business use at all,"
broader than the no-resale line Tom intended, and section 2(a) blocked
the very pull requests the same license already welcomes back in section
7. Sections 2(a) and 2(b) are rewritten: 2(a) now names the Licensor as
the one permitted recipient of a modified copy and says a pull request is
not distribution; 2(b) targets offering the plugin, or a lookalike built
from it, to third parties as a product or service, and says your own
business use is not restricted. Section 2(c) is unchanged. A five-line
plain-language block ("what you can do", "what you cannot do",
"contributions", "not open source", "third-party notices") now opens
every plugin `LICENSE` and its README `Licence` section, and this file,
above the per-part table. Every plugin repository gains a `CONTRIBUTING.md`
and a machine-readable `license` field in `package.json`:
`LicenseRef-ICOR-Source-Available-1.0`. The license family stays
source-available; this is a drafting fix, not a family change, decided
without a Fachanwalt read (Tom, 2026-09-06).

Applied to `icor-for-life-outliner`, `icor-for-life-planner`,
`icor-for-life-chat`, `icor-for-life-terminal`, `icor-for-life-interface`,
`icor-for-life-sqlite-viewer`, `icor-for-life-diagrams`,
`icor-for-life-scaffold-check`, `icor-for-life-connect`,
`icor-for-life-focus`, each in its own repository and release, and to this
repository's `LICENSE.md`. `icor-for-life-inkline` carried uncommitted
work at the time and is not yet included. No plugin build changed: the
license text is not part of `main.js`.

## 1.10.0

Released 2026-09-06.

### Changed: the Planner owns Habits as its own entity, the way it owns Routines

The 2026-09-04 change (folded into 1.7.2) put `cadence`, `cadence_days`,
`started_on` and the daily log on the My Life habit note itself. That was
one step short: the Planner plugin is about to write habit schedules the
same way it already writes Routines, and two notes holding the same
schedule fact is not SSOT. So
`06 AI Team/AI Team Knowledge/Guidelines/GL-1002-frontmatter-conventions.md`
splits the `habit` type in two:

- `habit` (`04 Inner World/My Life/Habits/`) goes back to meaning only:
  no required field, optional `name`, `status` (`active | paused |
  abandoned`), `planner_habit` (wikilink to the planner-habit note).
  `cadence`, `cadence_days` and `started_on` are removed from this type
  entirely, not kept as a hint that could drift from the real schedule.
  There is no `## Daily log` on this note any more.
- new `planner-habit` type for `02 Planner/Habits/`: required `name`,
  `cadence` (`daily | weekdays | weekly | monthly`), `status` (`active |
  paused | archived`); optional `cadence_days` (`mon..sun` codes, for
  `weekly`), `month_day` (`1..28`, for `monthly`), `started_on`,
  `linked_note` (wikilink back to the My Life habit note), `created_at`.
  Body carries `## Log` behind the `<!-- habit-log: schema=... -->`
  sentinel, exactly the table the My Life note used to hold.
- The Planner's habit import moves `cadence`, `cadence_days`,
  `started_on` and the log off an existing My Life habit note and onto
  its new `planner-habit` note, and sets `linked_note` back to it. A
  vault that has not run the import yet keeps working on the old shape
  until it does.

Alongside: `02 Planner/README.md`'s Habits paragraph now describes the
Planner-owned note and the optional My Life meaning note; the example
`04 Inner World/My Life/Habits/Daily Scratchpad writing.md` drops
`cadence` and `started_on` and gains a one-line pointer to where the
schedule now lives; `06 AI Team/AI Team Knowledge/Scripts/validate-scaffold.py`
now checks the `planner-habit` shape under `02 Planner/Habits/` (cadence,
status, cadence_days, month_day value sets) in place of the old habit
cadence check, watched red on a broken habit note before this commit.
`02 Planner/Routines/` and the `planner-routine` type are unchanged.

No file is removed or moved.

### Added: the ICOR for Life - Outliner plugin

**ICOR for Life - Outliner** (`icor-for-life-outliner`, 0.1.0) ships and is
enabled in this download: indent, outdent and move a bullet together with
everything under it, an Enter that knows about children, a cursor that
stays out of the bullet, and a select-all that climbs, with two settable
keyboard schemes (Tana and Heptabase) alongside the default. It replaces
the community Outliner plugin every earlier download bundled by hand.

The plugin joins `community-plugins.json` in Outliner's place and the
license table in `LICENSE.md`, under the ICOR for Life Source-Available
License (Code) v1.0; it bundles no third-party code (the three CodeMirror
packages it needs are declared external and supplied by Obsidian at
runtime, not bundled into `main.js`).

Every plugin in this vault is now an ICOR for Life plugin, first-party;
none of them is a third-party community install any more, so
`THIRD-PARTY-NOTICES.md` no longer carries a "Bundled community plugins"
section. What it still carries, and always will as long as the code
ships, are the open-source library notices bundled inside our own
plugins (Simple Icons, the Claude Agent SDK's bundled Zod and
OpenTelemetry, sql.js, xterm.js and its addons) - MIT and Apache notices
that are the license of code inside our own plugins, not a notice about
a third-party tool, and removing them would breach those licenses.

If you updated by hand: disable the community Outliner plugin before
enabling ICOR for Life - Outliner. Both bind `Tab` and `Enter` inside
lists, and Obsidian will not let two plugins answer the same key at
once. Any hotkey you set on the old plugin's commands does not carry
over; set it again on the new plugin's commands under Settings ->
Hotkeys.

### Removed: the third-party Outliner plugin

The Outliner community plugin (`obsidian-outliner`, 4.10.2, MIT),
bundled since the first download, leaves the vault; ICOR for Life -
Outliner replaces it.

- `.obsidian/plugins/obsidian-outliner/LICENSE`: removed with the third-party plugin; replaced by `.obsidian/plugins/icor-for-life-outliner/`
- `.obsidian/plugins/obsidian-outliner/main.js`: removed with the third-party plugin; replaced by `.obsidian/plugins/icor-for-life-outliner/main.js`
- `.obsidian/plugins/obsidian-outliner/manifest.json`: removed with the third-party plugin; replaced by `.obsidian/plugins/icor-for-life-outliner/manifest.json`
- `.obsidian/plugins/obsidian-outliner/styles.css`: removed with the third-party plugin; replaced by `.obsidian/plugins/icor-for-life-outliner/styles.css`
- `community-plugins.json` enables `icor-for-life-outliner` in place of `obsidian-outliner`; `LICENSE.md` drops the Outliner row and adds one for `icor-for-life-outliner`; `THIRD-PARTY-NOTICES.md` drops its "Bundled community plugins" section entirely, keeping only the ICOR-plugin library notices; `README.md` names the new plugin among the first-party suite and drops the community-plugin mention; the zip builder's `data.json` allowance and its plugin inventory no longer name `obsidian-outliner`.

## 1.9.1

Released 2026-09-06.

### Changed: the download publishes itself on every push

A push to `main` is now a release. A GitHub Actions workflow,
`.github/workflows/release.yml`, runs the manifest check, the structure
check and the red tests, tags the commit with the version in
`.icor-for-life/VERSION` (a tag never moves: a version re-pushed on new
bytes fails the run), builds the member zip from that tag through
`build-release-zip.sh` and every gate in it, creates the GitHub release as
a draft with this file's section as its notes, uploads the zip under a
fixed name and under its version plus this version's `manifest.json`,
publishes the release once every digest has been read back, and then
downloads the assets through the public URLs and compares the digests.
Every gate, including a full dry run of the builder, runs before the tag
exists, so a red never burns a version number. The member download on
app.myicor.com follows that URL, so it is current the moment the run is
green, with no store, no pointer and no deploy anywhere else. The workflow
file is stripped from the download by the builder's residue gate, beside
the builder itself.

The builder learned three things for this. It creates a missing local
mirror on its own, so a fresh machine can build. It stages an exact tag
when told to (`ICOR_SCAFFOLD_TAG`), and refuses a tag whose tree calls
itself another version. And it writes the zip reproducibly, one timestamp
for every entry and the entries in one fixed order, so the same tag with
the same plugin releases gives the same bytes and a re-run is compared
with what was published instead of overwriting it.

The manifest no longer describes the files the residue gate strips. A
member's vault never had them, and the Scaffold Check plugin was reporting
the two build scripts as missing from every vault. The manifest builder
reads the gate's own list instead of keeping a copy.

### Removed: the upload step

- `06 AI Team/AI Team Knowledge/Scripts/publish-release-zip.sh`: removed. The member download store it uploaded to and the pointer it moved are retired; the release workflow publishes to GitHub Releases and the download follows the latest release.

`.icor-for-life/README.md` describes the release contract as it is now:
bump `VERSION`, write the section here, rebuild the manifest, push `main`.

## 1.9.0

Released 2026-09-06.

### Added: Flint, the Obsidian platform specialist

The basic team grows from eight agents to nine. Flint knows the Obsidian
platform itself: what the documented plugin API allows, what the
community directory's automated review rejects, and what breaks on a
phone or on the next Obsidian release. He reads every plugin or theme
change that touches the Obsidian API, a manifest (`minAppVersion`,
`isDesktopOnly`, `versions.json`) or the release path before it ships,
walks the community.obsidian.md submission and its review flags, and
answers "can Obsidian do this" from the live API reference, naming the
sanctioned way when the obvious way is an undocumented hack. He advises
and reviews; he never writes the fix. The preview scan on
community.obsidian.md runs from the user's own developer dashboard;
Flint asks for it and never implies a scan that did not happen. Same
two-file shape as the other agents (SOP-1007), plus a dispatch shim and
an avatar in the INKLINE style. Nothing is removed or moved.

- `06 AI Team/Agents/Flint/AGENT.md`: the contract.
- `06 AI Team/Agents/Flint/Flint.md`: the bio.
- `.claude/agents/flint.md`: the dispatch shim, subagent type `flint`.
- `06 AI Team/AI Team Knowledge/Avatars/flint.png`: the avatar.
- `agent-index.md`, `CLAUDE.md`, Larry's contract name the new agent.

## 1.8.0

Released 2026-09-06.

### Changed: journal entries carry the ICOR type, `category` is retired

The journal schema now speaks the ICOR canon. Journaling in ICOR carries
exactly two things beyond the words: what KIND of entry it is, and what
it is ABOUT. The scaffold's old `category` field (insight, reflection,
log, meeting, idea, other) mixed both jobs and matched neither; it is
retired and replaced.

The new shape, for `type: journal` notes:

- `journal_type` (required): one of exactly four - `interaction`
  (anything involving another human), `note` (a shallow capture),
  `thought` (a deep capture), `milestone` (something crossed a
  threshold). There is never a fifth type; `GL-1003` teaches the four.
- `format` (optional): how the entry arrived - `text`, `voice`, `photo`,
  `meeting-notes`, `other`. Absent means text.
- `key_element` (optional): the entry's subject when it is about a Key
  Element. A Topic subject lives in `linked_topics`, as before.

`type: journal` itself is untouched; it stays the entity discriminator.

**If you have existing entries with `category`: nothing breaks.** The
scaffold never edits your data, `validate-scaffold.py` does not gate
journal frontmatter, and old entries keep working as untyped notes in
every Base and search. To bring an old entry into the new shape, replace
its `category` line with a `journal_type` line using the closest of the
four (insight/reflection/idea usually mean `thought`, log usually means
`note`, meeting means `interaction`); do it whenever you next touch the
entry, or all at once, or never. New entries get the new shape from the
script and carry no `category`.

Files changed, none removed or moved:

- `GL-1002`: the journal row requires `journal_type`, offers `format`
  and `key_element`, plus the ruling "Journal: the ICOR four".
- `GL-1003`: new section "Type and Subject" - the four types with their
  one-line meanings, the never-a-fifth rule, and what a subject is.
- `SOP-1003`: picking the type is a judgement step; the script call
  uses the new flags; step 4 sets `key_element`.
- `Scripts/new-journal-entry.py`: `--category` becomes `--journal-type`
  (gated to the four), plus optional `--format` (gated to the five).
  Path, filename and skeleton ownership are unchanged. An old
  `--category` call now fails loudly instead of writing a stale field.
- `Scripts/run-red-tests.py`: the journal guards test the new flags,
  plus a new red test for a bad `--format`.
- `04 Inner World/Journal/2026/08/2026-08-27_perfect-for-my-knowledge-system.md`:
  the example entry migrates (`category: insight` becomes
  `journal_type: thought`) as the worked example of the new shape.

### Added: `/checkpoint`, the session close you can type

Sessions end when you close the terminal, and the three-line "session
close ritual" in `CLAUDE.md` fired only when the model decided a session
was ending, which is to say rarely. `/checkpoint` is a command: it runs
`Scripts/checkpoint.py` for the facts (the last session log, the tasks
changed since it, every WiP folder with its age and whether an open task
still names it), closes the tasks that shipped, proposes the WiP folders
that can leave, writes the session log, has agents journal what they
learned, and refuses to end without today's log
(`checkpoint.py --assert-logged`). The weekly review uses the same script
at a 30-day window. `CLAUDE.md`'s close ritual now points at the command.

- `.claude/commands/checkpoint.md`: the command.
- `06 AI Team/AI Team Knowledge/Workstreams/WS-1005-checkpoint.md`: the procedure.
- `06 AI Team/AI Team Knowledge/Scripts/checkpoint.py`: the report and the gate; two red tests in `run-red-tests.py`.
- `CLAUDE.md`, `06 AI Team/Agents/Larry/AGENT.md`, `WS-1002`, `Scripts/README.md`: point at it.

## 1.7.3

Released 2026-09-04.

### Changed: ICOR for Life - Terminal moves from 0.1.1 to 0.1.2

The bundled **ICOR for Life - Terminal** plugin (`icor-for-life-terminal`)
is now 0.1.2 in the download, and that is the only change. Nothing in the
vault tree moves: the download is built from this tag and stages the
Terminal from its latest published release, so this section exists to make
the changelog and the tag say the same thing as the bytes.

Why 0.1.2 exists. The Obsidian directory's automated review of 0.1.1 left
two warnings standing, and 0.1.2 clears both without changing how the
terminal behaves, with one visible exception named below:

- The CSS lint warning on `text-decoration`. The `text-decoration-line`
  and `text-decoration-style` longhands that 0.1.1 introduced were still
  reported as only partially supported at the declared floor, because the
  review's baseline flags a styled or two-line decoration in any spelling.
  The stylesheet now carries only the plain single-keyword forms
  (`underline`, `overline`, `line-through`). The cost is confined to the
  DOM renderer, the fallback behind WebGL: it draws double, wavy, dotted
  and dashed underlines as a plain underline. The WebGL renderer, the
  default, draws decorations on its canvas and never reads these rules.
- The behaviour warning "Direct Filesystem Access: Uses the Node.js fs
  module". The plugin's only `fs` use was the executable check for
  `claude` and the Python interpreter. The import is gone: a candidate is
  now probed by running it with `--version` (no shell, no stdio, a 1.5 s
  timeout) and the verdict is remembered per path until settings are
  saved. No spawn path's arguments change beyond these probes; the helper
  still runs Python in isolated mode (`-I`), and every condition of the
  security review stands. The plugin's `SECURITY.md` lists the probes in
  its spawn inventory.

Acknowledged and unchanged, as in 0.1.1: the clipboard recommendation
(inherent to a terminal) and the licence warning (the plugin is
source-available on purpose; its README now says in plain words what the
licence allows and what it does not). The three release assets carry
GitHub artifact attestations, verified before this cut with
`gh attestation verify main.js --repo myICOR/icor-for-life-terminal`.

If you updated by hand: copy `main.js`, `manifest.json` and `styles.css`
from https://github.com/myICOR/icor-for-life-terminal/releases/tag/0.1.2
into `.obsidian/plugins/icor-for-life-terminal/` and reload the plugin.
No file is removed or moved in this version.

## 1.7.2

Released 2026-09-04.

### Added: the download publishes itself

`06 AI Team/AI Team Knowledge/Scripts/publish-release-zip.sh` is maintainer
tooling. It takes the zip the builder produced, refuses it unless its version
is the newest tag and its manifest is byte for byte that tag's manifest,
uploads it to the member download store under its version, downloads it back
and compares the digest, and only then moves the pointer the download is
served from. From this version on, the download a member gets is the version
git says is current, without a code change anywhere else. Like
`build-release-zip.sh`, the script is stripped from the download by the
builder's residue gate, so nothing in the vault tree changes for a member.
`.icor-for-life/README.md` names the step.

Until now the download was pinned by hand on the member app side, and 1.5.0,
1.6.0 and 1.7.0 were tagged while the download still served 1.4.2. 1.7.1 was
the first version published through the new step, and 1.7.2 is the first
whose release includes it.

### Changed: the frontmatter contract learns Routines and the full Habit shape

The ICOR for Life - Planner plugin is about to write habit check-ins and
routine logs into member vaults, and no plugin writes a field the Guideline
does not name. So
`06 AI Team/AI Team Knowledge/Guidelines/GL-1002-frontmatter-conventions.md`
changes ahead of that plugin release:

- `habit`: `cadence` is now `daily | weekdays | weekly | monthly | adhoc`
  (the singular `weekday` is accepted on read); optional `name`,
  `cadence_days` (lowercase `mon..sun`), `started_on` (`since` stays an
  alias on read). A new section documents the daily log as a body table
  behind the `<!-- habit-log: schema=streak -->` or `schema=process`
  sentinel, with the marker table; streaks are computed, never stored.
- new `planner-routine` type for `02 Planner/Routines/`: required `name`,
  `routine_type`, `start`, `end`, `weekdays`, `active`; optional
  `created_at`; body sections `## Steps` and `## Log` behind the
  `<!-- routine-log: schema=steps -->` sentinel.
- `planner-item` gains `created_at`, `parent_id`, `recurring`,
  `due_string`, `occurrences`, `reopen_pending`, `last_completed_due`,
  matching the Planner README's contract table.

Alongside: `02 Planner/README.md` gains a Routines and a Habits paragraph;
the example `04 Inner World/My Life/Habits/Daily Scratchpad writing.md`
shows `cadence_days` as a commented optional field and uses `started_on`;
`06 AI Team/AI Team Knowledge/Scripts/validate-scaffold.py` now checks
habit `cadence` and `cadence_days` values and the shape of every note in
`02 Planner/Routines/`. The folder itself is not a required room: the
Planner creates it when Routines are switched on.

No file is removed or moved.

## 1.7.1

Released 2026-09-04.

### Changed: ICOR for Life - Terminal moves from 0.1.0 to 0.1.1

The bundled **ICOR for Life - Terminal** plugin (`icor-for-life-terminal`)
is now 0.1.1 in the download. 1.7.0 shipped 0.1.0 and said 0.1.1 would
follow; this is that release, and it is the only change. Nothing in the
vault tree moves: the download is built from this tag and stages the
Terminal from its latest published release, so this section exists to
make the changelog and the tag say the same thing as the bytes.

Why 0.1.1 exists. The Obsidian directory's automated review of 0.1.0
returned one error and a set of warnings, and 0.1.1 answers them without
changing how the terminal behaves:

- The manifest error: the plugin description named the app. It is
  rewritten without the word, same meaning, in `manifest.json` and in the
  README's first paragraph.
- The deprecated `setWarning` call on the "Remove profile" button now uses
  `setDestructive` on Obsidian 1.13 and newer, and sets the old class
  below that.
- The multi-value `text-decoration` shorthands in xterm's stylesheet, which
  the CSS lint reported as only partially supported at the declared floor,
  are split into `text-decoration-line` and `text-decoration-style` when
  `styles.css` is assembled; a headless-Chrome test proves each xterm
  decoration class still resolves to the same computed style.
- The three release assets (`main.js`, `manifest.json`, `styles.css`) are
  now published by the plugin's own release workflow and carry GitHub
  artifact attestations. Anyone can verify what they downloaded with
  `gh attestation verify main.js --repo myICOR/icor-for-life-terminal`.

Acknowledged and unchanged: the licence warning (the plugin is
source-available on purpose, see its `LICENSE`) and the behaviour warnings
(file access outside the vault, process spawning, clipboard use are what a
terminal is; each is described in its `README.md` and `SECURITY.md`). The
security posture of 0.1.0 stands: the helper still runs Python in isolated
mode, and no new spawn path was added.

If you updated by hand: copy `main.js`, `manifest.json` and `styles.css`
from https://github.com/myICOR/icor-for-life-terminal/releases/tag/0.1.1
into `.obsidian/plugins/icor-for-life-terminal/` and reload the plugin.
No file is removed or moved in this version.

## 1.7.0

Released 2026-09-04.

### Added: the ICOR for Life - Terminal plugin

The shell inside the app is now our own. **ICOR for Life - Terminal**
(`icor-for-life-terminal`, 0.1.0) ships and is enabled in this download:
your login shell in a tab or a split, keyboard capture that still lets
Obsidian keep its palette, a find bar, clickable links, shell profiles,
and a one-command launcher for Claude Code in the vault folder ("Run
Claude Code here", "Resume a Claude session by ID"). It is skinned by the
INKLINE theme and hands a session to and from the AI Chat pane. Desktop
only. It makes no network connection of its own and scrubs the `CLAUDE*`
environment variables from the shell it starts; its `README.md` and
`SECURITY.md` inside the plugin folder state everything it does on your
machine. It passed the team's security review before release.

The download built from this tag carries Terminal 0.1.0; 0.1.1 (the
Obsidian directory's review fixes) follows in the next scaffold release.

Prerequisite, stated once in `README.md` first steps: the integrated pane
needs Python 3 on macOS (Xcode Command Line Tools or Homebrew) and on
Linux. On Windows this version has no integrated pane; it offers one
button that opens your own terminal in the vault folder.

The plugin joins `community-plugins.json`, the license table in
`LICENSE.md` (under the ICOR for Life Source-Available License (Code)
v1.0; it bundles xterm.js and five addons under MIT, listed in
`THIRD-PARTY-NOTICES.md`), the zip builder's release-staged set and
inventory, and the first-open workspace's ribbon entry. The manifest
builder lists it as an expected plugin from `community-plugins.json`.

### Removed: the third-party Terminal plugin

polyipseity's Terminal community plugin (`terminal`, 3.27.1, AGPL-3.0),
bundled since the first download, leaves the vault; ICOR for Life -
Terminal replaces it. If you updated by hand, disable `terminal` under
Settings -> Community plugins and delete its folder when convenient; the
Scaffold Check will point at the files. With it gone, no copyleft
component ships in this vault at all.

- `.obsidian/plugins/terminal/LICENSE.txt`: removed with the third-party plugin; replaced by `.obsidian/plugins/icor-for-life-terminal/`
- `.obsidian/plugins/terminal/data.json`: removed with the third-party plugin; the ICOR Terminal keeps its own settings in its own folder
- `.obsidian/plugins/terminal/main.js`: removed with the third-party plugin; replaced by `.obsidian/plugins/icor-for-life-terminal/main.js`
- `.obsidian/plugins/terminal/manifest.json`: removed with the third-party plugin; replaced by `.obsidian/plugins/icor-for-life-terminal/manifest.json`
- `.obsidian/plugins/terminal/styles.css`: removed with the third-party plugin; replaced by `.obsidian/plugins/icor-for-life-terminal/styles.css`
- `community-plugins.json` enables `icor-for-life-terminal` in place of `terminal`; `LICENSE.md` drops the AGPL row; `THIRD-PARTY-NOTICES.md` drops the polyipseity entry and lists the xterm.js components; `README.md` names the new plugin and the Python prerequisite; the zip builder's `data.json` allowance, plugin list and inventory no longer name `terminal`; the manifest builder no longer excludes its `data.json`.

## 1.6.0

Released 2026-09-04.

### Added: the 07 Databases room

The vault gains its eighth room, `07 Databases/`, the shelf for real
SQLite databases that have no markdown source: health archives, logs,
analytics stores. It ships empty except for its `README.md`; whatever
lands there is the member's own. One test decides what belongs: does
anything in the vault regenerate the database? Yes means it is a mirror
of the notes and does not belong (Bases and Obsidian search query the
notes directly); no means it is a source, and this is its home.

The room is owned by the **ICOR for Life - SQLite Viewer** plugin
(`icor-for-life-sqlite-viewer`), which opens every database read-only:
table browser, query console, dashboards built without SQL, on desktop,
phone and tablet (big databases render on the phone from a
desktop-computed cache). The plugin joins the expected suite in
`community-plugins.json`, the license table in `LICENSE.md`, and the
component notes in `THIRD-PARTY-NOTICES.md` (it bundles sql.js, MIT).
Its defaults point at `07 Databases/` from plugin version 0.5.0.

- `07 Databases/README.md`: the room's doctrine, for members.
- `validate-scaffold.py` now requires the room, so Scaffold Check
  reports it when missing.
- `GL-1001`, `GL-1004`, `README.md` and `CLAUDE.md` list the new room.

### Added: four more agents

The basic team grows from four agents to eight. Mack (automation: tool
connections, MCP servers, webhooks, automations, and the fetch half of
an import), Silas (structure and databases: frontmatter and structure
audits, Bases, the 07 Databases room, the shape of an import), Iris
(the design system: created with you on your first creative request,
never shipped as a default) and Charta (structured visuals:
infographics, tables, diagrams, carousels, PDFs from clean HTML) join
Larry, Penn, Pax and Nolan. Each arrives in the two-file shape of
SOP-1007, `AGENT.md` plus the bio `<Name>.md`, with a dispatch shim
under `.claude/agents/`.

All eight avatars are replaced with the INKLINE set: one orange marker
line on ink, a bust per agent (Larry fox, Penn barn owl, Pax magpie,
Nolan terrier, Mack beaver, Silas elephant, Iris hummingbird, Charta
peacock). The four existing files are overwritten in place under their
old names; nothing is removed or moved in this entry.

- `06 AI Team/Agents/Mack/`, `Silas/`, `Iris/`, `Charta/`: new, two
  files each.
- `.claude/agents/mack.md`, `silas.md`, `iris.md`, `charta.md`: new.
- `06 AI Team/AI Team Knowledge/Avatars/`: four new PNGs, four
  overwritten in place.
- `agent-index.md`, `CLAUDE.md`, Larry's contract, `WS-1004` (Mack
  fetches remote sources, Silas verifies) and `SOP-1013` (Mack runs the
  wiring steps) name the new agents.

### Fixed: binary captures can be stamped processed

Reported and designed by community member Mike Mather, 2026-09-04. Found
in live use: `Scripts/stamp-processed.py` read its note as UTF-8 before
any guard ran, so a scanned PDF ended in a `UnicodeDecodeError` traceback
instead of a refusal, and `--archive` only accepted notes inside
`01 Inbox/Outer World/`, so a scan in `01 Inbox/Scanner Inbox/` was out of
reach twice over. No binary capture on this scaffold had ever carried a
processed stamp, and two rules gave two answers for one scanned document:
GL-1001 keeps binaries in `05 Assets/` forever, hard rule 2 keeps
processed originals in `Outer World/archive/` forever. Two runs four days
apart resolved that tie two different ways, and neither was recorded.

The ruling, in `GL-1002` under "Binary captures and the processed stamp
(ruling 2026-09-04)": the wrapper note carries the stamp, and the move to
the shelf IS the archive. A binary capture is moved to `05 Assets/`, never
copied there, and never lands in `Outer World/archive/` as a second copy.

- `GL-1002` declares `processed`, `processed_summary` and
  `processed_into` optional on `type: document` and carries the ruling.
- `stamp-processed.py` gains a second route, `--capture <binary>`: a
  binary passed as the note is refused by name (suffix first, then a
  UTF-8 decode check, so neither route can traceback); `--capture` needs
  a binary inside `01 Inbox/` (a `.md` is told to use `--archive`); the
  wrapper's `source_file` must resolve to exactly one file under
  `05 Assets/`; the shelf copy must match the inbox original by sha256
  before the original is removed, and a mismatch removes nothing and
  stamps nothing; `--archive` and `--capture` refuse each other. The
  text route is unchanged.
- `SOP-1002` no longer contradicts itself: step 3 sent binaries to the
  shelf while step 6 archived every capture. Binaries now take the
  wrapper route in step 3, markdown captures archive in step 6.
- `CLAUDE.md` hard rule 2 carries the binary clause, so the boot file
  and the guideline agree.
- `run-red-tests.py` adds the binary-route guards (31 to 36), one of
  which asserts the inbox original survives a forced hash mismatch, plus
  a green control for a correct `--capture`.

Nothing is removed or moved in this entry.

### Removed: the ICOR for Life - Diagrams plugin

The fullscreen mermaid viewer is a switch inside **ICOR for Life -
Interface** from Interface 0.5.0 - same button, same modal - so the
separate plugin leaves the suite. If your vault still has it, Interface
detects it and you see one button either way; delete the old folder when
convenient.

- `.obsidian/plugins/icor-for-life-diagrams/`: removed; the viewer moved
  into `.obsidian/plugins/icor-for-life-interface/` (Diagrams switch).
- `community-plugins.json`, the zip builder's plugin list and inventory,
  `LICENSE.md` and `THIRD-PARTY-NOTICES.md` no longer name it.

## 1.5.0

Released 2026-09-01.

### Removed or moved

The three CSS snippets are gone from `.obsidian/snippets/`. Their rules moved
into the theme and the Interface plugin, so the vault no longer needs
`enabledCssSnippets` and it ships empty. If you updated by hand and still see
these files, delete them; nothing reads them any more, and leaving them enabled
in `appearance.json` paints rules twice.

- `.obsidian/snippets/icor-rooms.css` moved into the ICOR for Life - INKLINE theme (room colours and glyphs keyed on the room number)
- `.obsidian/snippets/icor-ribbon.css` moved into the ICOR for Life - INKLINE theme
- `.obsidian/snippets/icor-logo.css` moved into the ICOR for Life - Interface plugin (the two rules that need the file tree)
- `.obsidian/snippets/icor-scaffold.css` existed for one day, 2026-08-31, as the interim home of the two file-tree rules, and was replaced by the ICOR for Life - Interface plugin. Only a copy downloaded that day has it; delete it.

The theme now draws rooms, banner and ribbon itself, and the new
**ICOR for Life - Interface** plugin (shipped and enabled from this version)
provides the switches plus per-folder colour, icon and label under Settings.
On its first run in an ICOR vault it hides the ribbon and reduces the chrome
on its own, so nothing has to be configured to get the shipped look.

### Renamed: the shipped knowledge docs move to the 1001 range

Every Guideline, SOP and Workstream the scaffold ships is renumbered from
`NNN` to `1NNN`: `GL-001` becomes `GL-1001`, `SOP-013` becomes `SOP-1013`,
`WS-004` becomes `WS-1004`, and so on for all 23. Every wikilink, alias,
frontmatter `id` and script reference follows.

Why: the numbers `001` to `999` are yours. A vault that has grown its own
`GL-001` for a year would otherwise collide with the scaffold's `GL-001` the
day it updates, and two different documents under one name is the one
defect a copy-over cannot recover from. Reserving `1001` and up for the
shipped set means your numbering and the scaffold's never meet. Nobody
writes a thousand of their own.

If you updated by hand and still have the old `NNN` files: the Scaffold
Check plugin tells them apart from your own by content. A file with the old
name and the scaffold's old bytes is a leftover to delete; a file with the
old name and your bytes is yours, and stays.

### Added

- `.icor-for-life/`: the version folder. `VERSION` names this version,
  `manifest.json` describes it for machines, and this changelog describes it
  for people. The Scaffold Check plugin compares a vault against the latest
  manifest.
- `Scripts/build-scaffold-manifest.py` builds and checks the manifest.

### Changed

- The first-open workspace gate walks the whole workspace document instead of
  testing a remembered list of fields, so a personal note open in a pane or a
  search term left in a search box is refused the same way a listed path is.

## 1.4.2

2026-08-30. Seventh numbered state.

### Added

- `.obsidian/workspace.json`: one curated workspace whose only job is to open
  the README with the file tree beside it and the tour video at the top. Before
  this the first open landed on whatever Obsidian last felt like, which in
  practice was a third-party plugin's changelog.

### Changed

- The theme ships as `ICOR for Life - INKLINE`, and the vault selects it by
  that exact name, so the folder in `.obsidian/themes` and the name inside the
  theme agree.

## 1.4.1

2026-08-30. Sixth numbered state, patch.

### Changed

- The theme folder follows the theme's own name.

## 1.4.0

2026-08-30. Sixth numbered state.

### Added

- The vault opens with the ICOR for Life suite already in place: Planner,
  Focus, Diagrams, myICOR Connect and ICOR AI Chat installed and enabled, and
  ICOR for Life - INKLINE as the theme. Each plugin keeps its own settings file
  outside the vault's history, so keys and tokens stay on your machine.
- The licence page names every part of the download and what you may do with
  each one, under the names Obsidian shows in Settings.
- The download is checked before it is built: every plugin and the theme is
  compared byte for byte against its published release, and the vault must
  hold exactly the parts it is meant to hold.

## 1.3.1

2026-08-30. Fifth numbered state, patch.

### Changed

- Toolbar and sort behaviour as in 1.3.0, corrected.

## 1.3.0

2026-08-30. Fourth numbered state.

### Changed

- The toolbar above the file tree is settled: the two note-creation buttons,
  the Focus map and AI Team launchers, and Collapse all, which is now always
  present.

### Removed or moved

- Sorting is gone from the file-tree toolbar. The tree is ordered by the
  numbers the rooms carry, the same in every copy of this vault. Obsidian
  offers no other route to that control, so this removes the choice rather
  than moving it. No file was removed; the button was.

## 1.2.0

2026-08-30. Third numbered state.

### Changed

- The banner above the file tree publishes its distance from the left edge as
  a named value the theme reads, so the controls under it line up and move
  with it.
- The file tree's toolbar keeps only actions that act on the file tree. Note
  and folder creation moved to the command palette, where they are searchable
  and can take a hotkey.
- Room styling is keyed on the two-digit room number, never the full name, so
  a room can be renamed or translated and keeps its colour and glyph. The
  scaffold validator reads the room stylesheet to decide which folders to
  check instead of keeping its own copy of that rule.

## Before 1.2.0

Versions 1.0.0 and 1.1.0 predate this changelog and this repo's tag history
as kept here. Their release notes live on the GitHub releases page.
