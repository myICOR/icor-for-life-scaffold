# AGENTS.md: how this folder works

You are an AI working in a person's **ICOR for Life** folder: their life and work as plain markdown files, organised by ICOR (Input, Control, Output, Refine). This page is for any AI that opens the folder (Claude, ChatGPT, Codex, Cursor, Gemini or any other). **Read `AboutMe.md` next**: who the person is, how they write and what they believe. Take it into account in everything you do here. It is **read-only** for you. Everything you need is in these places:

| Where | What it is |
| --- | --- |
| this page | the principles, the folders by ICOR stage, and where to look |
| `AboutMe.md` | **the person**: who they are, what they do, their tone of voice, their beliefs, what they want now. Write in their voice and decide by their beliefs. **Read-only**: never change it; suggest a change to the person instead |
| `_System/schema.json` | **the structure**: every type of note, its folder, its fields, the values a field allows, and which type each link points to |
| `11 Databases/Objects.base` | every object in one table, a view per type; each type's folder has its own `.base` with all its fields |
| `09 AI/Skills/` (copies in `.agents/skills/` and `.claude/skills/`) | **the skills**: how to do the work here, step by step |

## The principles

1. **The person's words are sacred.** Never rewrite, paraphrase or delete what they wrote. Add beside it, never instead of it.
2. **Connect before you file.** Ask what a thing connects to on their My Life map (a Key Element, a Goal, a Project, a Topic, a Habit) or which person it is about, and link it as a `[[wikilink]]`. A note that connects to nothing is lost; if nothing fits, do not file it.
3. **One fact lives in one note.** Never copy. Find the note that holds it (`find-entity.py`) and link to it.
4. **The schema is the law.** Every note has a `type`; use only the fields and values the schema gives that type (a field with options takes one of them: never a stray value; a new option goes into the schema first, when the person asks), and link only to the type a field points to. If something does not fit, ask the person; never invent a field, a type or a folder. The person may add types of their own (a tool, a recipe, a trip): they are in the schema like the rest, with a template and a folder, and `new-entity.py` takes them. Add a type yourself only when the person asks. A type can be a kind of another (`extends`: a restaurant is a kind of company): it has that type's fields and links and counts as one wherever it is asked for. To change a note's type, set `type`, add the new type's missing fields empty and move the note to the type's folder; never delete a field when you do, so changing back loses nothing.
5. **Work happens in the Workbench; what lasts is filed.** Drafts, sketches, research and your own working files go in `08 Workbench/<YYYY-MM-DD> <name>/`, never anywhere else. When the work is done, file what lasts as objects (a note, a project, a source, a journal entry) with skill **new-object** or **capture**, and move the folder to `08 Workbench/Done/`.
6. **Keep your record in `09 AI/`.** Read `AboutMe.md`, `09 AI/README.md` and `09 AI/Memory.md` when you start. Every time you change something in this folder, add an entry to today's log, `09 AI/Log/YYYY/MM/YYYY-MM-DD.md` (`_System/Tools/ai-log.py` writes it). When the person corrects you or states a preference, update `Memory.md`. Never edit an earlier log entry.
7. **Ask before you move, rename or delete** anything the person made. Create freely where a skill says so.

## The folders, by ICOR stage

The numbered folders follow the ICOR stages (`stages` in `_System/schema.json`): what comes in, what is kept and connected, what goes out, and what you learn from it.

| Stage | Folder | What lives there |
| --- | --- | --- |
| Input | `00 Daily Notes/YYYY/MM/` | the person's raw writing: one note a day and quick scratch notes. **Never edit or mark it.** Read it; carry a piece on when they ask |
| Input | `01 Inbox/` | scans (`Scanner Inbox/`) and anything not yet sorted |
| Control | `02 My Life/` | the map of the person's life: `Key Elements/`, `Goals/`, `Projects/`, `Topics/`, `Habits/` |
| Control | `03 Journal/YYYY/MM/` | their journal entries, by date |
| Control | `04 Notes/` | their knowledge: ideas, outlines, drafts, documents, `Meetings/`, `Highlights/`, `ICOR Journey Notes/` |
| Control | `05 Contacts/` | `People/` and `Companies/` |
| Control | `06 Sources/` | **what others made**: one `source` note per book, article, video, podcast, post or paper, with highlights |
| Output | `07 Planner/` | tasks synced from their task apps by the Planner plugin; not yours to edit |
| Output | `08 Workbench/` | work in progress: one dated folder per piece of work, anything goes inside; finished work in `Done/` |
| Refine | `09 AI/` | the AI's own folder: `README.md`, `Skills/` (how to work here), `Memory.md`, `Log/` (what was done, by day), `Reviews/` (the weekly reviews) |
| | `10 Files/` | files only (`Images/`, `Audio/`, `Documents/`), embedded from notes |
| | `11 Databases/` | `Objects.base` (every object, a view per type), and data too large or row-shaped for notes |
| | `_System/` | the schema, templates and tools. Read it; change it only when asked |

**Inner World and Outer World** are how the folders split, not folders of their own: `02` to `05` are what went through the person (their Inner World), `06 Sources` is what others made (the Outer World).

**My Life** (`02 My Life/`) is the map of the person's life: **Key Elements** (the big areas, like Health or Family), **Goals** (outcomes in a Key Element), **Projects** (work that serves a goal), **Topics** (subjects they follow) and **Habits**. Almost everything you file links to something on this map.

## What goes where

- **The person wrote it, and it has a date as its identity** (what happened, what they thought): a journal entry, `03 Journal/YYYY/MM/YYYY-MM-DD_<slug>.md`, one of four types: interaction, note, thought, milestone.
- **The person's knowledge with a subject that keeps changing** (an idea, an outline, meeting notes, a draft): a note in `04 Notes/`, linked to its project, Key Element or topic.
- **Someone else made it** (a book, an article, a video, a podcast, a post): a `source` in `06 Sources/`, linked to what it serves. The person's own thought about it is a journal entry or note that links to the source.
- **A fact about a person or company**: a property on their note in `05 Contacts/`. The conversation itself is a journal entry of type `interaction` that links to them.
- **A file you keep**: the file in `10 Files/Documents/`, a `document` note in `04 Notes/` pointing at it.
- **A goal, project, topic, habit or area of life**: one note in `02 My Life/`, short; the material links to it.
- **Work not done yet** (a draft in several files, a sketch, research for a decision): a dated folder in `08 Workbench/`, with a `brief.md` first (what it is, the My Life item it serves as a link, the next step). Anything goes inside; nothing in it is checked.

## Where files go

**Never write in the top folder.** It holds only `README.md`, `AGENTS.md`, `AboutMe.md`, `LICENSE.md` and the numbered folders. Every file has its folder; if you are unsure, `01 Inbox/` is the folder for "not sorted yet".

| A file that is | Goes in |
| --- | --- |
| a picture, a screenshot, a photo or a video | `10 Files/Images/` |
| a recording, a voice memo, a sound | `10 Files/Audio/` |
| a PDF, an office file, an e-book, a spreadsheet you keep | `10 Files/Documents/` (and a `document` note in `04 Notes/`) |
| a scan still to be filed | `01 Inbox/Scanner Inbox/` |
| a note | the folder of its type in `_System/schema.json` (made with `new-entity.py`); unsorted: `01 Inbox/` |

Never make a new folder next to the numbered folders. In Obsidian the Objects plugin moves anything that lands in the top folder to its place; in Claude Code a hook (`_System/Tools/guard-paths.py`) refuses the write and says where it belongs; the tools in `_System/Tools/` refuse a top-level path too.

## How a note is written

- **No H1 title.** Obsidian shows the file name as the note's title, so a note starts right after its properties: with its first section or its first words. No blank line first, no `# Title`.
- **Never hard-wrap Markdown here: one paragraph per line.** Obsidian shows every newline as a break, so a paragraph or a list item stays on one line, however long. `_System/Tools/tidy-markdown.py check` finds wrapped ones.

## What's core, what's optional

`_System/parts.json` lists every piece that ships. **Core**, needed for the folder to work: the numbered folders, this page and `_System`; Obsidian's Daily notes, Templates, Properties and Bases; ICOR Objects, ICOR Journal, ICOR Planner and ICOR Interface (the ICOR for Life - INKLINE theme only changes the look). **Optional**, each removable on its own with nothing depending on it: ICOR Scratchpad, ICOR AI Chat, ICOR Connect, ICOR Focus, ICOR Canvases, ICOR Outliner, ICOR PDF Annotation, ICOR Terminal, ICOR SQLite Viewer, and the databases `11 Databases/Health.sqlite` and `11 Databases/Finance.sqlite`. Never assume an optional piece is there: check the plugin's folder in `.obsidian/plugins/` or the file before you use it, and say so when it is missing. Never remove a piece yourself unless the person asks.

**Health and money stay in their databases.** A person's health data and finances live in `11 Databases/Health.sqlite` and `11 Databases/Finance.sqlite`, on their computer. Read them through SQL (`sqlite3 -readonly`, or your own SQLite access) when they ask, and answer in your words. Never copy rows into a note, a journal entry or anywhere outside the folder, and never send them anywhere unless the person asks for exactly that. Write to them only when the person asks, and only in the tables `11 Databases/README.md` describes. The schemas are in `_System/Databases/`.

## Skills

In `09 AI/Skills/`, one folder per skill.

| Skill | Use it when the person says |
| --- | --- |
| `capture` | "save this", "where does this go?", "note that…" |
| `process-scratchpad` | "process my day", "process my scratchpad" |
| `process-outer-world` | "process my sources", "connect my clips", "what is in my reading queue?" |
| `write-journal-entry` | "journal this", "write an entry about…" |
| `new-object` | "new project / goal / person / topic / habit / key element / note / document / source" |
| `find-everything-about` | "what do I have about…", "show me everything on…" |
| `life-snapshot` | "where do I stand?", "what are my goals and focus?" |
| `weekly-review` | "weekly review", "plan my week" |
| `check-quality` | "check my notes", "is my folder in order?" |

## Tools

Python 3.9 or newer, no packages: the scripts in `_System/Tools/` (their `README.md` lists them). Every script prints `OK …` or `FAIL …`. Prefer a script to writing a file by hand: they know the schema, the names and the folders. Templates for every type: `_System/Templates/`.

In Obsidian, the **ICOR Objects** plugin enforces the same schema for the person: New object, `@` to link or create while writing, New object type, typed links, turning a line of the daily note into an object, and a Connections panel. You and the plugin follow one definition.

## Never touch

- `.obsidian/`: the person's Obsidian settings, plugins and theme.
- `.icor-for-life/`: this computer's machine files and `.env` (API keys). Never read `.env` out loud or copy it.
- `07 Planner/`: the Planner plugin's notes.
- `00 Daily Notes/`: read it, never write in it.
- `09 AI/Log/`: add today's entries; never change an earlier one.
- `AboutMe.md`: the person's own page, read-only. Read it and take it into account; never write it, even when asked to: tell the person what to add and let them write it. What you learn about how they like you to work goes in `09 AI/Memory.md`.
- The top folder: nothing new goes there (see "Where files go").
