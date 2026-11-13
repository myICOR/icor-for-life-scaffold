---
type: guideline
id: GL-1011
title: Date mentions link to daily notes
created: 2026-09-11
---

# GL-1011 Date mentions link to daily notes

> **A full date written in a note body is written as `[[YYYY-MM-DD]]` and
> resolves to that day's daily note. The script creates the daily note if
> it is missing.**

Checkable, so it is enforced by
`Scripts/link-dates-to-daily-notes.py` and not by asking nicely
([[GL-1005-code-vs-instructions|GL-1005]]).

## Why

An empty daily note is worth nothing on its own, and most daily notes are
close to empty: a few lines written in a hurry, or nothing at all. The same
note with forty backlinks is a different object. It is the timeline of
everything that touched that day, assembled by the vault rather than by
you: the journal entry, the meeting, the contact you met, the decision, the
brief that cites it. You get that for free the moment the date is a link,
and you get nothing at all while it stays text.

That is why the rule is about the mention and not about the daily note. You
never have to go and enrich a day. You write the date the way you were
going to write it anyway, in two more characters on each side, and the day
fills itself in.

## Scope: whose knowledge is this

**The daily note is a timeline of YOUR life and work, so only your own
notes link into it.** That is the whole scope rule, and everything below is
it applied.

The team's operating records stay bare on purpose. Session logs, specialist
journals and Team Knowledge are how the AI team remembers its own work, and
they are dense with dates: a session log alone carries a timestamp in its
name, its frontmatter and most of its lines. If those linked, every daily
note would fill up with the team's housekeeping and the day's real content
would be buried under it. A daily note should show you the journal entry,
the meeting, the contact and the brief, not the eleven times an agent
recorded that it ran a script.

**IN, the two rooms you write in and the script may write to**

| Room | Which files |
| --- | --- |
| `04 Inner World/` | all of it, except the protected text listed below |
| `03 WiP/` | all of it, except the protected text listed below |
| `01 Inbox/` | none: captures and the capture archive are out (since 2.3.0) |

**OUT: all of `06 AI Team/`, without exception.** Session logs, specialist
journals, Team Knowledge, SOPs, Guidelines, Workstreams, Tasks, Templates,
Scripts, AI Sessions. Also `00 Daily Scratchpad/` itself, `01 Inbox/`
(every capture, and `01 Inbox/Outer World/archive/`), `02 Planner/`,
`05 Assets/` and `07 Databases/`.

**Why the inbox is out.** Hard rule 1: what you wrote in a capture is never
edited, and two pairs of brackets are an edit. A capture's dates get their
links when it is processed: the note, journal entry or task it becomes
lives in one of the two rooms above. Before 2.3.0 the inbox was in scope
and a checkpoint's `--fix` rewrote captures and the archive.

**OUT inside the two rooms, never touched**

- **Your Original Text.** The `## Original Text` section of a journal entry
  ([[GL-1003-journal-entry-anatomy|GL-1003]]), from its heading down to the
  next heading of the same or a higher level, or to the end of the note.
  Hard rule 1 makes it sacred, so a date in it stays as you typed it. The
  `## Expansion` below it is linked as usual.
- **Blockquotes.** A line starting with `>`, and the lines that run on from
  it up to the next blank line. A quoted passage is someone's words, kept
  as they were.

- **YAML frontmatter.** A typed date there is data, not prose: `created`,
  `date`, `due`, `processed`. It is read by Bases and by every script, and
  a wikilink in a date field is a broken value. This is the one exception
  people ask about, so it is stated plainly: **frontmatter dates stay bare.**
- Fenced code blocks and inline backtick code.
- Anything already inside `[[...]]`, including an alias.
- Markdown link targets `(...)` and any URL.
- A date that is part of a longer token: a filename (`2026-09-11.md`), a
  slug (`2026-09-11-jeff-meyers`), an id (`tsk-2026-09-09-020`), a
  timestamp (`2026-09-11T14:12`, `2026-09-11-14-30`), a path.
- Any folder whose name starts with `_` (archives, snapshots, `_files`),
  `Templates/`, `INDEX.md`, `.obsidian/`, `node_modules/`.
- Month-only and year-only mentions. Only a full, real calendar date
  counts; `2026-13-45` is not one.

That second list matters as much as the first. About 114k `YYYY-MM-DD`
strings sit in a lived-in vault and almost none of them are prose. A rule
that is not this narrow would bury every note in brackets and teach you to
stop seeing links at all.

**One more condition.** `[[2026-09-11]]` only reaches the daily note while
no OTHER note in the vault is named `2026-09-11.md`. A second file with
that name makes the link ambiguous, so the script reports it as a collision
and leaves that date alone rather than writing a link that lands somewhere
unpredictable. The fix is to rename the other note: a journal entry is
`YYYY-MM-DD_<slug>.md` ([[GL-1004-naming-rules|GL-1004]]), never a bare
date.

## The script

```
Scripts/link-dates-to-daily-notes.py [<vault-root>]
    --check            list every unlinked mention, exit 1 if any (default)
    --dry-run          what --fix would do, with counts, no writes
    --fix              write the links, create the missing daily notes
    --since YYYY-MM-DD only dates on or after this day
    --path PATH        only this file or folder; repeatable
    --json             machine-readable
```

It reads the folder and the format from `.obsidian/daily-notes.json`, so a
vault that moved its daily notes still works, and it refuses to run on
`--fix` when that file is missing rather than guessing a room. It refuses
outright when the format's last segment is not `YYYY-MM-DD`, because a
`[[YYYY-MM-DD]]` link could not resolve to a note named anything else.
Created daily notes are blank, with no frontmatter and no template, exactly
as [[GL-1007-capture-and-where-things-go|GL-1007]] requires. Running
`--fix` twice changes nothing the second time.

## When it runs

- **Any agent may run `--fix` on the files it touched**, at any point, without
  asking. It is additive and idempotent, and it never reaches a capture, an
  Original Text section or a blockquote, so there is nothing protected for
  it to change.
- **Before the session log is written**, as part of the checkpoint. That is
  where the rule actually holds: the session's own notes get their links
  while the session still remembers what it wrote.
- `checkpoint.py` prints the count of unlinked mentions as one more row, and
  `checkpoint.py --assert-dates-linked` exits 1 when any remain.
- A historical backfill over years of old notes is a decision, not a chore.
  Run `--dry-run` first, read the numbers, then choose. `--since` exists so
  you can take it in bites.
