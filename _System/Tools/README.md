# Tools

The life scripts. Run from the folder's root with `python3 _System/Tools/<script> …`. Each prints `OK …` or `FAIL …` and knows the structure from `../schema.json` (`_System/schema.json`).

| Script | What it does |
| --- | --- |
| `new-entity.py` | creates one object (project, goal, person, note…) from its template, in its folder, linked: `new-entity.py note "Title" --link "[[Health]]" --set note_type=outline`; `--list` shows the types, also the ones you added |
| `new-journal-entry.py` | creates a journal entry with the person's words verbatim |
| `find-entity.py` | finds the note a name or alias belongs to, so one thing never gets two notes |
| `set-property.py` | sets or removes one property on one note, within the schema |
| `stamp-processed.py` | stamps an Inbox capture or a document note as processed and archives the capture (never a scratchpad) |
| `life-snapshot.py` | goals, focus projects, the week's priorities, today's highlight, Key Elements, active topics |
| `planner-week.py` | this week's priorities and daily highlight |
| `check-quality.py` | links, required and invented fields, allowed values, orphans, waiting captures |
| `link-dates-to-daily-notes.py` | turns written dates into links to that day's note |
| `new-base.py` | writes the Bases table view for a collection; also the schema reader the other scripts use |
| `open-in-obsidian.py` | opens a file in Obsidian |
| `migrate-to-3.py` | brings a 2.x folder to the 3.0 layout from this download: a dry run first, `--live` to do it; never deletes, never overwrites |
| `noteio-icor.py` | reads and writes notes without touching bytes it did not mean to (used by the others) |
