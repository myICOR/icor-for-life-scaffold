# ICOR for Life

Your life and your work in one folder of plain markdown files, organised by ICOR (Input, Control, Output, Refine). Everything is ready in Obsidian, and any AI you point at the folder knows how to work with you here.

## Start here

1. **Turn on the plugins.** Obsidian asks once whether you trust this folder's plugins: choose to trust them. They are the ICOR for Life plugins, made by myICOR.
2. **Write today.** Click the calendar icon (Open today's daily note) and write whatever is on your mind. Type `@` to link a person, project, topic or book as you write, or create it on the spot: `@person/Paco Cantero`, `@project/Learn Spanish`, `@book/Deep Work`. The Connections panel on the right shows the day line by line, each line ready to become a journal entry, a project or a note.
3. **Open your Journal** with the book icon: your entries as cards, your streak, and a question for today.
4. **Create something** with the shapes icon (New object): a goal, a project, a person, a book you are reading. You fill in only what it needs, and it lands in the right place. Missing a kind? `@tool` (or any word) adds it as a type of your own.
5. **Find your objects** in `05 Databases/Objects.base`: all of them in one table, and a view per type (Projects, People, your Tools…). Each type's folder has its own table with all its fields. Delete one with the command Delete this object.
6. **Bring in your AI.** Open this folder in Claude, Codex, Cursor, Gemini or another AI that works with files. It reads `AGENTS.md` and knows the folders, the rules and the skills.

## The folders, by ICOR stage

| Stage | Folder | What it holds |
| --- | --- | --- |
| Input | `00 Daily Notes` | your post-it: one note a day, deliberately messy, and quick scratch notes |
| Input | `01 Inbox` | scans and anything not yet sorted |
| Control | `02 Inner World` | what went through you: Journal, Notes, Contacts, My Life |
| Control | `03 Outer World` | what others made: books, articles, videos, podcasts, with your highlights |
| Control | `04 Assets` | images, audio and documents |
| Control | `05 Databases` | the tables: `Objects.base` (every object), and data your notes cannot hold |
| Output | `06 Planner` | your tasks, synced by the Planner plugin |

Refine has no folder: you refine with the plugins (AI Chat, Connect, Focus) and in your weekly review.

**My Life** (in `02 Inner World`) is the map of your life: Key Elements, Goals, Projects, Topics and Habits. Everything you write connects to something on it, so you can find it again.

**Only what lasts goes in.** Work in progress stays in the tools where you do it; the result comes in when it is done.

The notes tagged `example` show how each kind of note looks. Keep them as long as they help, then delete them.

## What's core, what's optional

Everything comes installed and turned on, the way we use it ourselves. Some of it is the core: the folder needs it to work. The rest is optional: remove any of it and nothing else breaks. `_System/parts.json` lists the same.

**Core.** The numbered folders, `AGENTS.md` and `_System`; Obsidian's own Daily notes, Templates, Properties and Bases; and four plugins: ICOR for Life - Objects (objects, typed links, the type badge, the top folder kept clear), ICOR for Life - Journal, ICOR for Life - Planner (your week in 06 Planner) and ICOR for Life - Interface (the folders in their stage colours). The ICOR for Life - INKLINE theme is how it looks; any other theme works too.

**Optional.** To remove a plugin: Settings, Community plugins, turn it off, then delete its folder in `.obsidian/plugins/`. To remove a database: delete the file.

| Optional | What it gives you | Without it |
| --- | --- | --- |
| ICOR for Life - Scratchpad | a floating window for today's note or a scratch note | Obsidian's Daily notes still opens today |
| ICOR for Life - AI Chat | a chat with your AI inside the vault | your AI still works with the folder from outside |
| ICOR for Life - Connect | your app.myicor.com account in the vault | no myICOR dashboards or synced reflections |
| ICOR for Life - Focus | a map of where your attention goes | no Focus map |
| ICOR for Life - Canvases | ink and shapes on canvases | Obsidian's own canvases still open |
| ICOR for Life - Outliner | lists that behave like an outline | plain lists |
| ICOR for Life - PDF Annotation | highlights on PDFs as notes | the highlight notes you made stay |
| ICOR for Life - Terminal | a terminal inside the vault | no terminal tab |
| ICOR for Life - SQLite Viewer | opens the databases in 05 Databases | any SQLite tool still reads them |
| `05 Databases/Health.sqlite` | your health data, on this computer | nothing else changes |
| `05 Databases/Finance.sqlite` | your money, on this computer | nothing else changes |

Keeping your health or your finances here? The two databases stay on this computer, never in a note, and are yours to fill. `05 Databases/README.md` says what goes in each. Deleted one and want it back, empty: `python3 _System/Tools/new-database.py health` (or `finance`).

## Good to know

- **Your files stay yours.** Plain text in a folder on your computer: no account, no database, no lock-in. Back it up like any folder; Obsidian Sync, iCloud and Dropbox all carry it.
- **The look:** Settings, ICOR for Life - Interface: Gradient or Flat, and where a note's properties show (on top, folded, under the note, or only in the right sidebar).
- **`_System`** holds the structure, templates, skills and tools your AI and the plugins use. It is hidden in the file tree and kept out of search and the quick switcher; ICOR for Life - Interface shows it.

## Learn the method

[The ICOR Journey](https://app.myicor.com/journey) on myICOR: the courses this folder puts into practice.

ICOR for Life is an experiment from Tom's Tool Lab: it may change from one release to the next. MIT licence, see `LICENSE.md`.
