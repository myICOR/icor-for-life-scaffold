---
name: process-scratchpad
description: Carry the person's Daily Scratchpad (their raw daily notes) into its homes in the ICOR for Life folder - journal entries, notes, contacts, My Life - and stamp it processed. Use when they say "process my day", "process my scratchpad", or at the end of the day.
---

# Process the Daily Scratchpad

The scratchpad is `00 Daily Scratchpad/YYYY/MM/YYYY-MM-DD.md` (and quick captures `YYYYMMDDHHmm.md` in the same
month folder). It is the person's raw record: **you never edit its text**. You read it, create notes elsewhere, and
stamp it.

1. **Find what is waiting**: scratchpad notes without `processed: true` in their frontmatter, today's first. Ask before
   you take on earlier days.
2. **Read it piece by piece.** For each piece decide, with skill **capture**:
   - a thing that happened or a thought, with today as its identity → a journal entry (skill **write-journal-entry**;
     the person's words go verbatim under `## Original Text`)
   - knowledge about a subject → a note in `04 Inner World/Notes/`
   - a fact about a person → a property on their contact note
   - a new project, goal, topic, habit → skill **new-object** (ask first; these are commitments)
   - a task → tell the person; it belongs in their task app (the Planner plugin syncs it into `02 Planner/`)
   - nothing connects → leave it; it stays in the raw record
3. **Link everything** you create to its Project, Key Element, Topic or person.
4. **Stamp the scratchpad**:
   `python3 _System/Tools/stamp-processed.py "00 Daily Scratchpad/YYYY/MM/YYYY-MM-DD.md" --summary "<one line>" --into "[[<note 1>]]" --into "[[<note 2>]]"`
5. **Dates**: `python3 _System/Tools/link-dates-to-daily-notes.py --fix --path "04 Inner World"` turns written dates into links to the day.
6. **Report** in a short list: what you created, what you updated, and any question for the person last.
