# AGENTS.md: how this folder works

You are an AI working in a person's **ICOR for Life** folder: their life and work as plain markdown files, organised
by ICOR (Input, Control, Output, Refine). This page is for any AI that opens the folder (Claude, ChatGPT, Codex,
Cursor, Gemini or any other). Everything you need is in three places:

| Where | What it is |
| --- | --- |
| this page | the principles, the rooms, and where to look |
| `_System/schema.json` | **the structure**: every type of note, its folder, its fields, the values a field allows, and which type each link points to |
| `07 Databases/Objects.base` | every object in one table, a view per type; each type's folder has its own `.base` with all its fields |
| `_System/Skills/` (copies in `.agents/skills/` and `.claude/skills/`) | **the skills**: how to do the work here, step by step |

## The principles

1. **The person's words are sacred.** Never rewrite, paraphrase or delete what they wrote. Add beside it, never
   instead of it.
2. **Connect before you file.** Ask what a thing connects to on their My Life map (a Key Element, a Goal, a Project,
   a Topic, a Habit) or which person it is about, and link it as a `[[wikilink]]`. A note that connects to nothing is
   lost; if nothing fits, do not file it.
3. **One fact lives in one note.** Never copy. Find the note that holds it (`find-entity.py`) and link to it.
4. **The schema is the law.** Every note has a `type`; use only the fields and values the schema gives that type, and
   link only to the type a field points to. If something does not fit, ask the person; never invent a field, a type
   or a folder. The person may add types of their own (a tool, a recipe, a trip): they are in the schema like the
   rest, with a template and a folder, and `new-entity.py` takes them. Add a type yourself only when the person asks.
   A type can be a kind of another (`extends`: a restaurant is a kind of company): it has that type's fields and links
   and counts as one wherever it is asked for. To change a note's type, set `type`, add the new type's missing fields
   empty and move the note to the type's folder; never delete a field when you do, so changing back loses nothing.
5. **Only what lasts comes in.** Work in progress (drafts, research, an agent's working files) stays where the work
   happens: your harness, your project folder, the tool you work in. When it is done, file the result here as an object
   (a note, a project, a source, a journal entry) with skill **new-object** or **capture**. No temporary folders.
6. **Ask before you move, rename or delete** anything the person made. Create freely where a skill says so.

## The rooms

| Folder | What lives there |
| --- | --- |
| `00 Daily Scratchpad/YYYY/MM/` | the person's raw writing, one note a day. **Never edit its text.** Read it, process it, stamp it |
| `01 Inbox/` | scans (`Scanner Inbox/`) and anything not yet sorted |
| `02 Planner/` | tasks synced from their task apps by the Planner plugin; not yours to edit |
| `04 Inner World/` | **what went through the person**: `Journal/`, `Notes/`, `Contacts/`, `My Life/` |
| `05 Assets/` | files only (`Images/`, `Audio/`, `Documents/`), embedded from notes |
| `06 Outer World/` | **what others made**: one `source` note per book, article, video, podcast, post or paper, with highlights |
| `07 Databases/` | `Objects.base` (every object, a view per type), and data too large or row-shaped for notes |
| `_System/` | the schema, templates, skills and tools. Read it; change it only when asked |

**My Life** (`04 Inner World/My Life/`) is the map of the person's life: **Key Elements** (the big areas, like
Health or Family), **Goals** (outcomes in a Key Element), **Projects** (work that serves a goal), **Topics**
(subjects they follow) and **Habits**. Almost everything you file links to something on this map.

## What goes where

- **The person wrote it, and it has a date as its identity** (what happened, what they thought): a journal entry,
  `04 Inner World/Journal/YYYY/MM/YYYY-MM-DD_<slug>.md`, one of four types: interaction, note, thought, milestone.
- **The person's knowledge with a subject that keeps changing** (an idea, an outline, meeting notes, a draft): a note
  in `04 Inner World/Notes/`, linked to its project, Key Element or topic.
- **Someone else made it** (a book, an article, a video, a podcast, a post): a `source` in `06 Outer World/`, linked to
  what it serves. The person's own thought about it is a journal entry or note that links to the source.
- **A fact about a person or company**: a property on their note in `Contacts/`. The conversation itself is a
  journal entry of type `interaction` that links to them.
- **A file you keep**: the file in `05 Assets/Documents/`, a `document` note in `Notes/` pointing at it.
- **A goal, project, topic, habit or area of life**: one note in `My Life/`, short; the material links to it.

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

Python 3.9 or newer, no packages: the scripts in `_System/Tools/` (their `README.md` lists them). Every script prints
`OK …` or `FAIL …`. Prefer a script to writing a file by hand: they know the schema, the names and the folders.
Templates for every type: `_System/Templates/`.

In Obsidian, the **ICOR for Life - Objects** plugin enforces the same schema for the person: New object, `@` to link
or create while writing, New object type, typed links, turning a line of the daily note into an object, and a
Connections panel. You and the plugin follow one definition.

## Never touch

- `.obsidian/`: the person's Obsidian settings, plugins and theme.
- `.icor-for-life/`: this computer's machine files and `.env` (API keys). Never read `.env` out loud or copy it.
- `02 Planner/`: the Planner plugin's notes.
- `00 Daily Scratchpad/` text: only its processed stamp is yours.
