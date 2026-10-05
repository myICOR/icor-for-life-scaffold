# myPKA

> **ICOR for Life continues as myPKA 7.** Since October 2026 this folder and
> the AI team ship again as one download, under the name it started with:
> myPKA. Get the whole folder from the myPKA releases:
> https://github.com/myICOR/myPKA/releases/latest (or from Tom's Tool Lab
> on myICOR). This repository keeps the rooms, templates, guidelines, life
> scripts and the Obsidian setup that go into it.

## Start here: the tour

A walkthrough of the folder: what each room is for, how the AI team works
with you, and how to get your first session running.

![Watch the tour](https://youtu.be/GLO1voinujQ)

If the player does not appear, open it here: https://youtu.be/GLO1voinujQ

Learn it properly in the free **myPKA course**:
https://app.myicor.com/courses/mypka-system

## What myPKA is

myPKA stands for My Personal Knowledge Assistance. It is your life and your
work in **one folder of plain markdown files**, organised by ICOR (Input,
Control, Output, Refine), with an **AI team** that works in that folder with
you.

- **Your files stay yours.** Plain text in a folder on your own computer. No
  account, no database, no lock-in. Any editor opens it, any backup keeps it.
- **One place for everything.** Notes, journal, contacts, goals, projects,
  tasks, work in progress and the data your notes cannot hold. Business and
  personal side by side.
- **An AI team, not a chatbot.** Larry, the orchestrator, listens to you and
  hands each job to the specialist who owns it. Every agent has a written
  contract, every routine a written procedure (SOP), so the team behaves the
  same way tomorrow as today, with any AI model.
- **Works with any AI, and without one.** Claude Code, Codex, Gemini CLI,
  Cursor, or any AI chat that can read and write files. Everything also
  works by hand.

## Your AI team

You talk to **Larry**. He decides who does the work and never does a
specialist's job himself.

| Agent | What they do |
| --- | --- |
| Larry | The orchestrator: your one entry point; routes, plans with you, sums up |
| Penn | Knowledge processor: scratchpads, inbox captures, journal entries, filing into your Inner World |
| Nolan | HR: hires a new specialist when a job has no owner |
| Pax | Researcher: outside facts, web research, checks before action |
| Mack | Automation: tool connections (MCP, API, webhooks), automations, imports from a service |
| Silas | Structure and databases: properties, Bases, the vault health checks, the shape of an import |
| Iris | Design system: creates and guards your visual style |
| Charta | Structured visuals: infographics, tables, diagrams, one-pagers, PDFs |
| Flint | Obsidian platform: plugins, themes, what the Obsidian API allows |
| Ada | Planning and audit: written plans for bigger jobs, drift checks of the team's own machinery |
| Mason | Plugin contributor: turns a plugin bug or wish into a fix and a pull request |
| **Vex** | Security reviewer: reviews anything you did not write before it runs (an MCP server, a plugin, a script, a pack, a new dependency) and audits your app's security; proves, never applies the fix |
| **Felix** | Frontend developer: builds, fixes and audits web UI in your own code projects; code stays outside the folder |
| **Vera** | Quality gate: checks a visual or a web UI against your design system, WCAG 2.2 AA and the reader's needs; APPROVED, CONDITIONAL or BLOCKED |
| **Pixel** | Image maker: thumbnails, social images, covers, illustrations, agent avatars in your own look, or a ready image brief when no image generator is connected |

Vex, Felix, Vera and Pixel were separate agent packs until myPKA 7. They are
part of the team now. The full roster, with when to route to whom, is in
`06 AI Team/Agents/agent-index.md`. Need a role nobody covers? Ask Larry:
Nolan hires them.

## Use it with any AI. Obsidian is optional

The folder is the product. Nothing in it needs Obsidian.

- **With an AI tool:** open the folder in Claude Code, Codex, Gemini CLI or
  Cursor (the folder that holds `AGENTS.md`) and say hello to Larry.
  `AGENTS.md` is the one entry file every tool reads; the host files in
  `.claude/`, `.codex/` and `.gemini/` give each tool the team's agents and
  skills.
- **With an AI chat:** any assistant that can read and write the files of a
  folder can work here. Point it at `AGENTS.md` first.
- **With no AI at all:** the folder works fully by hand. Its scripts need
  Python 3.9 or newer and nothing else (on Windows, type `py -3` where a
  command says `python3`).

**If you like Obsidian**, open the folder as a vault and click "Trust author
and enable plugins". Twelve ICOR for Life plugins are **pre-installed** and
switch on: Planner, Focus, Connect, AI Chat, Interface, Scaffold Check,
SQLite Viewer, Terminal, Outliner, PDF Annotation, Canvases and Scratchpad.
The folder opens in the INKLINE theme. You can switch any plugin off, or
ignore Obsidian completely: the plugins only add an interface on top of the
same files.

## What is inside

| Room | What it holds |
| --- | --- |
| `00 Daily Scratchpad/` | Your post-it. One note per day, written by you, deliberately messy. Never deleted. The team extracts from it on your command. |
| `01 Inbox/` | The hand-over point. Anything you give to the AI team lands here and gets processed out. Outer-world captures (web clips, scans, voice memos) arrive in `Outer World/` and survive, stamped, in its `archive/`. |
| `02 Planner/` | Your real task list, synced. One note per open item from Todoist, ClickUp, flagged email and calendar, tended by the Planner plugin. The team plans and executes from here. |
| `03 WiP/` | The workbench. Work goes into one of four topic folders (Workstreams, AI Team, Projects, Operations), dated inside it; finished work retires to `_archive/`. |
| `04 Inner World/` | Everything that went through you: Contacts, Journal, Notes, and My Life (Goals, Key Elements, Topics, Projects, Habits). |
| `05 Assets/` | The binary shelf: images, audio, documents. Notes embed them; no knowledge lives here. |
| `06 AI Team/` | The team: agent contracts, shared knowledge (SOPs, Workstreams, Guidelines, Scripts), tasks, session logs and Expansions. |
| `07 Databases/` | The data shelf. SQLite databases with no markdown source. Ships empty. |

## Expansions

`06 AI Team/Expansions/` holds optional add-ons that are not switched on.
Its `README.md` lists them. Ask Larry: "I want the Designer Pack. Inspect it,
explain what it adds and install it." Your AI explains each step and asks
before it copies anything. Some of these packs were written for the older
folder layout (myPKA 5, ICOR for Life 1.x); their note says so, and your AI
adapts them to this folder with you before it installs anything.

## Start in five minutes

1. Unzip the download into a folder of your own, for example
   `Documents/myPKA`.
2. Open that folder in your AI tool and say: "Hello Larry, show me around."
   Or open it in Obsidian as a vault and trust the author.
3. Write into today's Daily Scratchpad, then tell Larry: "process my
   scratchpad". No AI at hand? Carry the pieces into their homes yourself;
   the walkthrough is `06 AI Team/AI Team Knowledge/Guidelines/GL-1007-capture-and-where-things-go.md`,
   "Doing it by hand, step by step".
4. Something someone else made? Clip it into `01 Inbox/Outer World/` with
   one line of why. The Web Clipper template in
   `06 AI Team/AI Team Knowledge/Templates/web-clipper-outer-world.json`
   does it in one click.
5. Learn the five ways of taking a note:
   `06 AI Team/AI Team Knowledge/Guidelines/GL-1010-the-five-capture-workflows.md`.

## Updating

**From myPKA 6 with ICOR for Life 2 in one folder (mode A):** download
`mypka-7.0.0.zip`, check it (below), then from your folder run, first as a
dry run, then with `--live`:

```
python3 "06 AI Team/AI Team Knowledge/Scripts/mypka-update.py" --release mypka-7.0.0.zip
python3 "06 AI Team/AI Team Knowledge/Scripts/mypka-update.py" --release mypka-7.0.0.zip --product icor
```

The first brings the team (Vex, Felix, Vera and Pixel included), the second
the rooms and guidelines. Nothing you edited is overwritten: where a file
you changed has a newer version, it lands next to yours as `<file>.update`.
Nothing is ever deleted.

**Vex, Felix, Vera or Pixel already installed as a pack?** Before the
update, ask your AI to remove the pack the way its README says
(`expansion-pack.py remove <name> --approved`): it deletes only files you
never edited, and your journal and `AGENT.local.md` stay. The update then
brings the team version.

**From myPKA 5 or ICOR for Life 1.x:** start a fresh folder from this
download and move your notes over with Larry. `MIGRATING-FROM-5.md` in the
myPKA repository has the steps.

The **Scaffold Check** plugin (in Obsidian) compares your folder with the
latest release and reports what is missing, what changed upstream and what
you edited yourself. It only looks; it never changes anything.

### Check that a download is genuine

Every release zip carries a build-provenance attestation. Before you unpack
a download, check it with the GitHub CLI (`gh`), as one line:

```
gh attestation verify mypka-<version>.zip --repo myICOR/myPKA --signer-workflow myICOR/myPKA/.github/workflows/release-mypka.yml --source-ref refs/tags/v<version> --deny-self-hosted-runners
```

Use the download only if it prints that verification succeeded.

## Learn the concepts

- [The myPKA course](https://app.myicor.com/courses/mypka-system): how the
  team works with your files, and how to build your own system.
- [The ICOR Journey](https://app.myicor.com/icor-journey): the courses this
  folder puts into practice.
- [Inner World and Outer World](https://app.myicor.com/lessons/inner-world-and-outer-world-697):
  the one lesson that explains this folder's deepest split.

## An experiment from Tom's Tool Lab

myPKA is something Tom (Thomas Roedl) builds and uses himself, and shares as
a starting point and as inspiration, not as a finished product.

- It may change from one release to the next. There is no support schedule,
  no promise of bug fixes and no feature release cycle.
- **You are responsible** for what you install and run, for its security,
  and for how you use it in your own systems. Back up your files first. If
  you are not sure what a step does, ask your AI to explain it, or do not
  run it.
- Questions and ideas: under the myPKA videos on myICOR.

## License

MIT. See `LICENSE.md`. The INKLINE theme, the libraries some plugins bundle
and our names and logos keep their own terms, listed there and in
`THIRD-PARTY-NOTICES.md`.
