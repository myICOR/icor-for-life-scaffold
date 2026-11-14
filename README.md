# ICOR for Life

Your life and your work in **one folder of plain markdown files**, organised
by ICOR (Input, Control, Output, Refine). ICOR for Life is a **content
folder**: the rooms, the templates, the guidelines, the Bases views, the
life scripts and the Obsidian settings that put the ICOR methodology into
practice. It holds your knowledge; it does not hold an AI team.

- **Your files stay yours.** Plain text in a folder on your own computer. No
  account, no database, no lock-in. Any editor opens it, any backup keeps it.
- **One place for everything.** Notes, journal, contacts, goals, projects,
  habits, work in progress and the data your notes cannot hold. Business and
  personal side by side.
- **Works by hand, with any AI, and with or without Obsidian.** Every
  guideline says how to do the step yourself.

**Looking for an AI team?** Agent teams come from **myPKA 8**, a separate
download that keeps its own folder. It is not part of this folder and does
not need it. Until myPKA 7, the two shipped as one folder; since ICOR for
Life 2.3.0 they do not.

## What is inside

| Room | What it holds |
| --- | --- |
| `00 Daily Scratchpad/` | Your post-it. One note per day, written by you, deliberately messy. Never deleted. You carry the pieces into their homes when you process it. |
| `01 Inbox/` | The hand-over point. Outer-world captures (web clips, scans, voice memos) arrive in `Outer World/` and survive, stamped, in its `archive/` once you have filed them. |
| `02 Planner/` | Your real task list, synced. One note per open item from Todoist, ClickUp, flagged email and calendar, tended by the Planner plugin. |
| `03 WiP/` | The workbench. Work goes into one of four topic folders (Workstreams, AI Team, Projects, Operations), dated inside it; finished work retires to `_archive/`. |
| `04 Inner World/` | Everything that went through you: Contacts, Journal, Notes, and My Life (Goals, Key Elements, Topics, Projects, Habits). |
| `05 Assets/` | The binary shelf: images, audio, documents. Notes embed them; no knowledge lives here. |
| `06 AI Team/AI Team Knowledge/` | The rules the folder runs on: Guidelines, Templates, Workstreams, the brand, and the life scripts (`Scripts/`). The room keeps its name so every path stays the same; no agents live here. |
| `07 Databases/` | The data shelf. SQLite databases with no markdown source. Ships empty. |

## Start in five minutes

1. Unzip the download into a folder of your own, for example
   `Documents/ICOR for Life`.
2. Open it in Obsidian as a vault, or in any editor. In Obsidian, add the
   plugins you want (see "Install the ICOR for Life plugins" below).
3. Write into today's Daily Scratchpad. Then carry the pieces into their
   homes: the walkthrough is
   `06 AI Team/AI Team Knowledge/Guidelines/GL-1007-capture-and-where-things-go.md`,
   "Doing it by hand, step by step".
4. Something someone else made? Clip it into `01 Inbox/Outer World/` with
   one line of why. The Web Clipper template in
   `06 AI Team/AI Team Knowledge/Templates/web-clipper-outer-world.json`
   does it in one click.
5. Learn the five ways of taking a note:
   `06 AI Team/AI Team Knowledge/Guidelines/GL-1010-the-five-capture-workflows.md`.

## Use it with AI, or without

The folder is the product. Nothing in it needs Obsidian or an AI.

- **With no AI at all:** the folder works fully by hand. Its scripts need
  Python 3.9 or newer and nothing else (on Windows, type `py -3` where a
  command says `python3`). `06 AI Team/AI Team Knowledge/Scripts/README.md`
  lists them.
- **With an AI chat or tool:** any assistant that can read and write the
  files of a folder can work here. Point it at this README and at
  `06 AI Team/AI Team Knowledge/Guidelines/` first; the guidelines are the
  rules it should follow.
- **With an agent team:** that is myPKA 8, a separate download in its own
  folder.

**If you like Obsidian**, open the folder as a vault. The folder ships no
plugins: you pick the ones you want from Obsidian's community directory,
and Obsidian keeps them up to date.

### Install the ICOR for Life plugins

1. Open Obsidian, then **Settings** (the gear, bottom left).
2. Go to **Community plugins**. If Obsidian asks, choose **Turn on community
   plugins**.
3. Click **Browse** and search for **ICOR for Life**.
4. Open each plugin you want, click **Install**, then **Enable**.

The plugins are Planner, Focus, Connect, AI Chat, Scaffold Check, Terminal,
Outliner, PDF Annotation, Canvases and Scratchpad. Interface and SQLite
Viewer are not in the directory yet; until they are, take `main.js`,
`manifest.json` and `styles.css` from the latest release on
[github.com/myICOR/icor-for-life-interface](https://github.com/myICOR/icor-for-life-interface/releases/latest)
or
[github.com/myICOR/icor-for-life-sqlite-viewer](https://github.com/myICOR/icor-for-life-sqlite-viewer/releases/latest)
and put them in `.obsidian/plugins/icor-for-life-interface/` or
`.obsidian/plugins/icor-for-life-sqlite-viewer/`.

For the look: **Settings**, **Appearance**, **Themes**, **Manage**, search
for **INKLINE**, then **Install and use**.

Every plugin is optional. The folder works without any of them, and without
Obsidian: the plugins only add an interface on top of the same files.

## Updating

**A folder you started from myPKA 7 (ICOR for Life 2.2.x inside it):** the
updater that came with that folder still updates its ICOR for Life content.
Download `icor-for-life-obsidian-edition-<version>.zip`, check it (below),
then from your folder run it first as a dry run, then with `--live`:

```
python3 "06 AI Team/AI Team Knowledge/Scripts/mypka-update.py" --release icor-for-life-obsidian-edition-<version>.zip --product icor
```

It writes only ICOR for Life's own files. **Your myPKA 7 files stay exactly
as they are**: `AGENTS.md`, `.mypka/`, `.claude/`, `.codex/`, `.gemini/` and
the team in `06 AI Team/` are not part of this release, so the update never
touches them, and it never deletes anything. Nothing you edited is
overwritten: where a file you changed has a newer version, it lands next to
yours as `<file>.update`. If you move to myPKA 8 later, it lives in its own
folder; your myPKA 7 files can stay or go as you decide.

**Plugins you already have** stay where they are and stay switched on: the
update leaves `.obsidian/plugins/` and your list of enabled plugins alone.
From ICOR for Life 2.3.0 they update from Obsidian's community directory
(Settings, Community plugins, Check for updates), not from the download.

**A folder with no updater in it:** unzip the new release beside it and carry
over what changed; the **Scaffold Check** plugin (from the community
directory) compares your folder with the latest release and reports what is
missing, what changed upstream and what you edited yourself. It only looks;
it never changes anything.

**From ICOR for Life 1.x or myPKA 5:** start a fresh folder from this
download and move your notes over.

### Check that a download is genuine

Every release zip carries a build-provenance attestation. Before you unpack
a download, check it with the GitHub CLI (`gh`), as one line, with your
version in place of `<version>`:

```
gh attestation verify icor-for-life-obsidian-edition-<version>.zip --repo myICOR/icor-for-life-scaffold --signer-workflow myICOR/icor-for-life-scaffold/.github/workflows/release.yml --source-ref refs/tags/<version> --deny-self-hosted-runners
```

Use the download only if it prints that verification succeeded.

## Learn the concepts

- [The ICOR Journey](https://app.myicor.com/icor-journey): the courses this
  folder puts into practice.
- [Inner World and Outer World](https://app.myicor.com/lessons/inner-world-and-outer-world-697):
  the one lesson that explains this folder's deepest split.

## An experiment from Tom's Tool Lab

ICOR for Life is something Tom (Thomas Roedl) builds and uses himself, and
shares as a starting point and as inspiration, not as a finished product.

- It may change from one release to the next. There is no support schedule,
  no promise of bug fixes and no feature release cycle.
- **You are responsible** for what you install and run, for its security,
  and for how you use it in your own systems. Back up your files first. If
  you are not sure what a step does, do not run it.
- Questions and ideas: on myICOR.

## License

MIT. See `LICENSE.md`. Our names and logos keep their own terms, listed
there. The plugins and the INKLINE theme are not part of this download; each
carries its own license and notices in its repository.
