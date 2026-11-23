# AGENTS.md: how this folder works

You are an AI working in a person's **ICOR for Life** folder: their life and work as plain markdown files, organised by ICOR (Input, Control, Output, Refine). This page is for any AI that opens the folder (Claude, ChatGPT, Codex, Cursor, Gemini or any other). Everything you need is in three places:

| Where | What it is |
| --- | --- |
| this page | the principles, the folders by ICOR stage, and where to look |
| `_System/schema.json` | **the structure**: every type of note, its folder, its fields, the values a field allows, and which type each link points to |
| `05 Databases/Objects.base` | every object in one table, a view per type; each type's folder has its own `.base` with all its fields |
| `_System/Skills/` (copies in `.agents/skills/` and `.claude/skills/`) | **the skills**: how to do the work here, step by step |

## The principles

1. **The person's words are sacred.** Never rewrite, paraphrase or delete what they wrote. Add beside it, never instead of it.
2. **Connect before you file.** Ask what a thing connects to on their My Life map (a Key Element, a Goal, a Project, a Topic, a Habit) or which person it is about, and link it as a `[[wikilink]]`. A note that connects to nothing is lost; if nothing fits, do not file it.
3. **One fact lives in one note.** Never copy. Find the note that holds it (`find-entity.py`) and link to it.
4. **The schema is the law.** Every note has a `type`; use only the fields and values the schema gives that type (a field with options takes one of them: never a stray value; a new option goes into the schema first, when the person asks), and link only to the type a field points to. If something does not fit, ask the person; never invent a field, a type or a folder. The person may add types of their own (a tool, a recipe, a trip): they are in the schema like the rest, with a template and a folder, and `new-entity.py` takes them. Add a type yourself only when the person asks. A type can be a kind of another (`extends`: a restaurant is a kind of company): it has that type's fields and links and counts as one wherever it is asked for. To change a note's type, set `type`, add the new type's missing fields empty and move the note to the type's folder; never delete a field when you do, so changing back loses nothing.
5. **Only what lasts comes in, and nothing here is yours.** Work in this folder the way an outside tool would through MCP or an API: read how it works, then file results as objects (a note, a project, a source, a journal entry) with skill **new-object** or **capture**. Drafts, research, memory and your own working files stay with you, outside the folder. No temporary folders, no folder of your own.
6. **Ask before you move, rename or delete** anything the person made. Create freely where a skill says so.

## The folders, by ICOR stage

The numbered folders follow the ICOR stages (`stages` in `_System/schema.json`): what comes in, what is kept and connected, what goes out. Refine has no folder: it happens in the plugins (AI Chat, Connect, Focus) and in the weekly review, and you do it from outside the folder.

| Stage | Folder | What lives there |
| --- | --- | --- |
| Input | `00 Daily Notes/YYYY/MM/` | the person's raw writing: one note a day and quick scratch notes. **Never edit or mark it.** Read it; carry a piece on when they ask |
| Input | `01 Inbox/` | scans (`Scanner Inbox/`) and anything not yet sorted |
| Control | `02 Inner World/` | **what went through the person**: `Journal/`, `Notes/`, `Contacts/`, `My Life/` |
| Control | `03 Outer World/` | **what others made**: one `source` note per book, article, video, podcast, post or paper, with highlights |
| Control | `04 Assets/` | files only (`Images/`, `Audio/`, `Documents/`), embedded from notes |
| Control | `05 Databases/` | `Objects.base` (every object, a view per type), and data too large or row-shaped for notes |
| Output | `06 Planner/` | tasks synced from their task apps by the Planner plugin; not yours to edit |
| | `_System/` | the schema, templates, skills and tools. Read it; change it only when asked |

**My Life** (`02 Inner World/My Life/`) is the map of the person's life: **Key Elements** (the big areas, like Health or Family), **Goals** (outcomes in a Key Element), **Projects** (work that serves a goal), **Topics** (subjects they follow) and **Habits**. Almost everything you file links to something on this map.

## What goes where

- **The person wrote it, and it has a date as its identity** (what happened, what they thought): a journal entry, `02 Inner World/Journal/YYYY/MM/YYYY-MM-DD_<slug>.md`, one of four types: interaction, note, thought, milestone.
- **The person's knowledge with a subject that keeps changing** (an idea, an outline, meeting notes, a draft): a note in `02 Inner World/Notes/`, linked to its project, Key Element or topic.
- **Someone else made it** (a book, an article, a video, a podcast, a post): a `source` in `03 Outer World/`, linked to what it serves. The person's own thought about it is a journal entry or note that links to the source.
- **A fact about a person or company**: a property on their note in `Contacts/`. The conversation itself is a journal entry of type `interaction` that links to them.
- **A file you keep**: the file in `04 Assets/Documents/`, a `document` note in `Notes/` pointing at it.
- **A goal, project, topic, habit or area of life**: one note in `My Life/`, short; the material links to it.

## Where files go

**Never write in the top folder.** It holds only `README.md`, `AGENTS.md`, `LICENSE.md` and the numbered folders. Every file has its folder; if you are unsure, `01 Inbox/` is the folder for "not sorted yet".

| A file that is | Goes in |
| --- | --- |
| a picture, a screenshot, a photo or a video | `04 Assets/Images/` |
| a recording, a voice memo, a sound | `04 Assets/Audio/` |
| a PDF, an office file, an e-book, a spreadsheet you keep | `04 Assets/Documents/` (and a `document` note in `02 Inner World/Notes/`) |
| a scan still to be filed | `01 Inbox/Scanner Inbox/` |
| a note | the folder of its type in `_System/schema.json` (made with `new-entity.py`); unsorted: `01 Inbox/` |

Never make a new folder next to the numbered folders. In Obsidian the Objects plugin moves anything that lands in the top folder to its place; in Claude Code a hook (`_System/Tools/guard-paths.py`) refuses the write and says where it belongs; the tools in `_System/Tools/` refuse a top-level path too.

## How a note is written

- **No H1 title.** Obsidian shows the file name as the note's title, so a note starts right after its properties: with its first section or its first words. No blank line first, no `# Title`.
- **Never hard-wrap Markdown here: one paragraph per line.** Obsidian shows every newline as a break, so a paragraph or a list item stays on one line, however long. `_System/Tools/tidy-markdown.py check` finds wrapped ones.

## What's core, what's optional

`_System/parts.json` lists every piece that ships. **Core**, needed for the folder to work: the numbered folders, this page and `_System`; Obsidian's Daily notes, Templates, Properties and Bases; ICOR for Life - Objects, ICOR for Life - Journal, ICOR for Life - Planner and ICOR for Life - Interface (the ICOR for Life - INKLINE theme only changes the look). **Optional**, each removable on its own with nothing depending on it: ICOR for Life - Scratchpad, ICOR for Life - AI Chat, ICOR for Life - Connect, ICOR for Life - Focus, ICOR for Life - Canvases, ICOR for Life - Outliner, ICOR for Life - PDF Annotation, ICOR for Life - Terminal, ICOR for Life - SQLite Viewer, and the databases `05 Databases/Health.sqlite` and `05 Databases/Finance.sqlite`. Never assume an optional piece is there: check the plugin's folder in `.obsidian/plugins/` or the file before you use it, and say so when it is missing. Never remove a piece yourself unless the person asks.

**Health and money stay in their databases.** A person's health data and finances live in `05 Databases/Health.sqlite` and `05 Databases/Finance.sqlite`, on their computer. Read them through SQL (`sqlite3 -readonly`, or your own SQLite access) when they ask, and answer in your words. Never copy rows into a note, a journal entry or anywhere outside the folder, and never send them anywhere unless the person asks for exactly that. Write to them only when the person asks, and only in the tables `05 Databases/README.md` describes. The schemas are in `_System/Databases/`.

## Skills

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

In Obsidian, the **ICOR for Life - Objects** plugin enforces the same schema for the person: New object, `@` to link or create while writing, New object type, typed links, turning a line of the daily note into an object, and a Connections panel. You and the plugin follow one definition.

## Never touch

- `.obsidian/`: the person's Obsidian settings, plugins and theme.
- `.icor-for-life/`: this computer's machine files and `.env` (API keys). Never read `.env` out loud or copy it.
- `06 Planner/`: the Planner plugin's notes.
- `00 Daily Notes/`: read it, never write in it.
- The top folder: nothing new goes there (see "Where files go").
