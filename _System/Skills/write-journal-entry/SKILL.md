---
name: write-journal-entry
description: Write a journal entry in the ICOR for Life folder the ICOR way - one of four types (interaction, note, thought, milestone), the person's words verbatim, linked to the people, topics, projects and Key Element it is about. Use when they say "journal this", "write an entry about…", or tell you about their day.
---

# Write a journal entry

An entry is created on purpose, never as a side effect. It lives at
`04 Inner World/Journal/YYYY/MM/YYYY-MM-DD_<slug>.md` (slug: 3 to 6 words, lowercase, hyphens).

## Pick the type (exactly one of four, never a fifth)

| type | when |
| --- | --- |
| `interaction` | anything with another person: a call, a meeting, a conversation worth keeping |
| `note` | something noticed and written down, no deep thinking |
| `thought` | real thinking: a reflection, an insight, a decision worked through |
| `milestone` | something crossed a threshold: a first, a finish, a number reached |

If it seems to fit none, it is usually two entries, or a `note`.

## Write it

`python3 _System/Tools/new-journal-entry.py --date YYYY-MM-DD --slug <slug> --journal-type <type> --original "<their exact words>"`
(add `--format voice|photo|meeting-notes|other` when it did not arrive as typed text).

Then in its frontmatter (fields in `_System/schema.json`, type `journal`):
- `linked_people`, `linked_topics`, `linked_projects`: lists of `"[[Name]]"`
- `key_element: "[[Health]]"` when it is about a Key Element (a quoted wikilink; a bare name is not a link)
- `mood` if they said how they felt

## The two sections

- `## Original Text`: their words, **verbatim, forever**. Never edit, shorten or "improve" them.
- `## Expansion`: what you add, marked as yours by living here: context you know, connections you see.

A person's story lives in the journal; their contact note only holds properties.
