# ICOR for Life

Your life and your work in one folder of plain markdown files, organised by ICOR (Input, Control, Output, Refine). Everything is ready in Obsidian, and any AI you point at the folder knows how to work with you here.

## Start here

1. **Turn on the plugins.** Obsidian asks once whether you trust this folder's plugins: choose to trust them. They are the ICOR for Life plugins, made by myICOR.
2. **Write today.** Click the calendar icon in the ribbon on the left (Open today's daily note) and write whatever is on your mind. Type `@` to link a person, project, topic or book as you write, or create it on the spot: `@person/Paco Cantero`, `@project/Learn Spanish`, `@book/Deep Work`. The Connections panel on the right shows the day line by line, each line ready to become a journal entry, a project or a note.
3. **Open your Journal** with the book icon in the ribbon: your entries as cards, your streak, and a question for today.
4. **Create something** with the shapes icon in the ribbon (New object): a goal, a project, a person, a book you are reading. You fill in only what it needs, and it lands in the right place. Missing a kind? `@tool` (or any word) adds it as a type of your own.
5. **Find your objects** in `11 Databases/Objects.base`: all of them in one table, and a view per type (Projects, People, your Tools…). Each type's folder has its own table with all its fields. Delete one with the command Delete this object.
6. **Bring in your AI.** Open this folder in Claude, Codex, Cursor, Gemini or another AI that works with files. It reads `AGENTS.md` and knows the folders, the rules and the skills.

## The folders, by ICOR stage

| Stage | Folder | What it holds |
| --- | --- | --- |
| Input | `00 Daily Notes` | your post-it: one note a day, deliberately messy, and quick scratch notes |
| Input | `01 Inbox` | scans and anything not yet sorted |
| Control | `02 My Life` | the map of your life: Key Elements, Goals, Projects, Topics and Habits |
| Control | `03 Journal` | your journal entries, by date |
| Control | `04 Notes` | your ideas, outlines, drafts, documents and meeting notes |
| Control | `05 Contacts` | people and companies |
| Control | `06 Sources` | what others made: books, articles, videos, podcasts, with your highlights |
| Output | `07 Planner` | your tasks, synced by the Planner plugin |
| Output | `08 Workbench` | where you work: one folder per piece of work, messy on purpose |
| Refine | `09 AI` | your AI's record: what it did, what it learned about you, your weekly reviews |
| | `10 Files` | images, audio and documents |
| | `11 Databases` | the tables: `Objects.base` (every object), and data your notes cannot hold |

**My Life** is the map of your life. Everything you write connects to something on it, so you can find it again.

**Inner World and Outer World.** `02` to `05` are what went through you: your Inner World. `06 Sources` is what others made: the Outer World. The split is in the order of the folders, not in an extra level.

**Work in the Workbench, keep what lasts.** Start a folder in `08 Workbench` for anything you are working on: a plan, a draft, a sketch, research for a decision. Write a `brief.md` first (what it is, what it serves, the next step). When it is done, what lasts becomes a note, a journal entry or a project update, and the folder moves to `Done/`.

**Your AI keeps a log.** Any AI that works here writes what it did in `09 AI/Log/`, one file a day, and keeps what it learned about you in `09 AI/Memory.md`. Change AI tools and the record stays with you.

The notes tagged `example` show how each kind of note looks. Keep them as long as they help, then delete them.

## What's core, what's optional

Everything comes installed and turned on, the way we use it ourselves. Some of it is the core: the folder needs it to work. The rest is optional: remove any of it and nothing else breaks. `_System/parts.json` lists the same.

**Core.** The numbered folders, `AGENTS.md` and `_System`; Obsidian's own Daily notes, Templates, Properties and Bases; and four plugins: ICOR Objects (objects, typed links, the type badge, the top folder kept clear), ICOR Journal, ICOR Planner (your week in 07 Planner) and ICOR Interface (the folders in their stage colours). The ICOR for Life - INKLINE theme is how it looks; any other theme works too.

**Optional.** To remove a plugin: Settings, Community plugins, turn it off, then delete its folder in `.obsidian/plugins/`. To remove a database: delete the file.

| Optional | What it gives you | Without it |
| --- | --- | --- |
| ICOR Scratchpad | a floating window for today's note or a scratch note | Obsidian's Daily notes still opens today |
| ICOR AI Chat | a chat with your AI inside the vault | your AI still works with the folder from outside |
| ICOR Connect | your app.myicor.com account in the vault | no myICOR dashboards or synced reflections |
| ICOR Focus | a map of where your attention goes | no Focus map |
| ICOR Canvases | ink and shapes on canvases | Obsidian's own canvases still open |
| ICOR Outliner | lists that behave like an outline | plain lists |
| ICOR PDF Annotation | highlights on PDFs as notes | the highlight notes you made stay |
| ICOR Terminal | a terminal inside the vault | no terminal tab |
| ICOR SQLite Viewer | opens the databases in 11 Databases | any SQLite tool still reads them |
| `11 Databases/Health.sqlite` | your health data, on this computer | nothing else changes |
| `11 Databases/Finance.sqlite` | your money, on this computer | nothing else changes |

Keeping your health or your finances here? The two databases stay on this computer, never in a note, and are yours to fill. `11 Databases/README.md` says what goes in each. Deleted one and want it back, empty: `python3 _System/Tools/new-database.py health` (or `finance`).

## Good to know

- **Your files stay yours.** Plain text in a folder on your computer (and, if you keep them, two SQLite files in 11 Databases): no account, no lock-in. Back it up like any folder; Obsidian Sync, iCloud and Dropbox all carry it.
- **The look:** Settings, ICOR Interface: Gradient or Flat, and where a note's properties show (on top, folded, under the note, or only in the right sidebar).
- **`_System`** holds the structure, templates, skills and tools your AI and the plugins use. It is hidden in the file tree and kept out of search and the quick switcher; ICOR Interface shows it.
- **The icons are in the ribbon.** Every ICOR for Life plugin keeps its icon in the ribbon on the left. Right-click the ribbon to reorder or hide icons. Two of them fold the file tree: Collapse all folders, and Show the open note in the file tree. The file tree's own row of buttons is hidden; ICOR Interface's settings bring it back.

## Learn the method

[The ICOR Journey](https://app.myicor.com/journey) on myICOR: the courses this folder puts into practice.

ICOR for Life is an experiment from Tom's Tool Lab: it may change from one release to the next. MIT licence, see `LICENSE.md`.
