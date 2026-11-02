---
type: guideline
id: GL-1002
title: Frontmatter conventions
created: 2026-08-27
---

# GL-1002 Frontmatter conventions

Frontmatter properties ARE the relations in this scaffold. Wikilinks in
frontmatter connect entities; Obsidian Bases read them as live tables.
**No agent may invent a field.** If a field you need is missing, update
this guideline first, then use it.

## Common fields (every note the team creates)

```yaml
type:        # one of the types below
created:     # ISO date
tags: []     # optional, lowercase, hyphenated
```

In Obsidian this frontmatter is the Properties panel at the top of the
note. A wikilink in a list property (`projects`, `linked_topics`,
`people`, and the like): add a list item, type `[[`, pick the note from
the suggestions. `Health` without brackets is text, not a link;
`[[Health]]` is the link. Every type a person files by hand has a
template in `06 AI Team/AI Team Knowledge/Templates/` (the `template`
column below; Templates: Insert template puts it in). The template is the
one place the field list is spelled out as YAML; this table names the
fields and their values, and never repeats the block. The moves, step by
step: [[GL-1007-capture-and-where-things-go|GL-1007]] "Doing it by hand".

## Per type

| type | required fields | optional fields | template |
| --- | --- | --- | --- |
| journal | date, journal_type (interaction/note/thought/milestone) | format (text/voice/photo/meeting-notes/other; absent = text), key_element (wikilink), mood, linked_people, linked_topics, linked_projects, source | `[[Templates/journal]]` |
| scratchpad | date | processed, processed_summary, processed_into, source (text, what wrote the note: `icor-chat` on a note saved from Chat), session_ids (the Chat sessions the note came from; Chat's resume reads it) | none: the daily note is blank by design |
| capture | source_url, captured (ISO datetime) | author, published, my_thought (the user's one-or-two-sentence thought, filled in the Web Clipper popup), processed, processed_summary, processed_into | `Templates/web-clipper-outer-world.json` (the Web Clipper, not Obsidian's Templates) |
| person | name | role, relation, companies, aliases, email, birthday, last_contact, next_action | `[[Templates/person]]` |
| company | name | industry, people, website | `[[Templates/company]]` |
| note | note_type (reference/idea/outline/meeting/draft/other); at least one of projects / key_elements / topics | projects, key_elements, topics, people, companies (wikilink lists), source_url, consumed (boolean; both only meaningful on `reference`), transcript (a URL or a wikilink to the transcript, whatever tool made it; only meaningful on `meeting` and `other`), transcribed_by (text, the tool), ai_summary (text, the model id), audio_retained (boolean; those three only meaningful on `meeting`), idea_status (open/promoted/parked/dropped; only meaningful on `idea`) | `[[Templates/note]]` |
| document | doc_type (contract/invoice/receipt/id/certificate/statement/letter/manual/other), source_file (wikilink to the binary in 05 Assets/Documents, MANDATORY) | projects, key_elements, topics (wikilink lists), preview_image, issued_on, expiry_date, amount, currency, people, companies, processed, processed_summary, processed_into | `[[Templates/document]]` |
| goal | status (not-achieved/achieved) | target_date, key_elements, workstreams (wikilink list to the Workstream notes that carry the goal; ruling 2026-09-15) | `[[Templates/goal]]` |
| pdf-highlight | highlight_id, source_file (wikilink to the PDF), page, anchor (selection/rect), rects, color, created, cssclasses | document (wikilink to the `document` wrapper note), selection (selection anchors), quote, image (rect anchors), canvases, linked_notes (both plugin-owned) | none: the plugin writes it |
| key-element | - | people, goals | `[[Templates/key-element]]` |
| topic | - | related_topics | `[[Templates/topic]]` |
| project | status (active/done/paused/dropped), goal (wikilink, MANDATORY) | start_date, end_date, external_links, key_elements, focus_rank (1, 2 or 3; absent means not in focus, at most three projects carry it), workstreams (wikilink list to the Workstream notes the project runs through; ruling 2026-09-15) | `[[Templates/project]]` |
| habit | - | name, status (active/paused/abandoned), planner_habit (FULL-PATH wikilink to the `planner-habit` note, `[[02 Planner/Habits/X]]`) | `[[Templates/habit]]` |
| icor-reflection | myicor_id (uuid), category, reflected_at (ISO date) | quality_score (0-100), pinned, synced_at (ISO datetime) | none: the plugin writes it |
| planner-item | source, external_id, title, status (open/done), priority (1-5) | due, url, tags, source_status, planned_day, planned_half, planned_order, done_local, weekly_goal (pins the item to the week; label: pinned, never goal), linked_note (one wikilink to a project note, plan-owned), synced_at, done_at, created_at, parent_id, recurring, due_string, occurrences, reopen_pending, last_completed_due | none: the plugin writes it |
| planner-routine | name, routine_type (morning/afternoon/evening), start (HH:MM), end (HH:MM, after start), weekdays (mon..sun codes), active (true/false) | created_at (ISO datetime) | none: the plugin writes it |
| planner-habit | name, cadence (daily/weekdays/weekly/monthly), status (active/paused/archived) | cadence_days (mon..sun codes, weekly), month_day (1-28, monthly), started_on (ISO date), linked_note (FULL-PATH wikilink to the My Life habit note, `[[04 Inner World/My Life/Habits/X]]`), created_at (ISO datetime) | none: the plugin writes it |
| planner-week | week (ISO week, YYYY-Www, matching the filename) | created_at (ISO datetime) | none: `Scripts/planner-week.py` |

Team types (task, session-log, progress-report, hire-proposal, sop, workstream, guideline, journal-entry, agent, agent-bio, agent-soul) and the agent and skill fields live in myPKA's GL-1015 Team frontmatter conventions since the split (2026-09-24).

## Journal: the ICOR four (ruling 2026-09-06)

`type: journal` stays the entity discriminator; `journal_type` says which
of the four ICOR kinds the entry is. The four values are exact, lowercase,
and closed: interaction, note, thought, milestone. What each means, and
why there is never a fifth, is taught in
[[GL-1003-journal-entry-anatomy|GL-1003]]. `format` records how the entry
arrived (absent means text). `key_element` is the entry's subject when it
is about a Key Element - a quoted wikilink, `key_element: "[[Health]]"`,
the same value shape goals and projects already use. A Topic subject
lives in `linked_topics` as before.
`category` is retired from the journal type: entries that still carry it
keep working as untyped, but no new entry gets one.

## Notes: notes and the wrapper-note pattern (ruling 2026-08-29, extended 2026-09-09)

`04 Inner World/Notes/` is one flat folder, one note per subject, and
it holds ICOR's one atomic unit, the Note. Two types share it. A plain
note is `type: note`; a document is a note with a file attached,
`type: document`, and lives in the same folder, because a file you keep
is not a second kind of thing in the method. Which of the two a note is
gets decided by one question: is there a binary behind it? Yes:
`document`. No: `note`. Where a note goes at all, against the Journal
and the other rooms, is taught in
[[GL-1007-capture-and-where-things-go|GL-1007]].

**`type: note`.** `note_type` is required and closed: `reference` (a
saved source you did not write: a video, an article, a paper),
`idea` (a thing you might do, gathering thoughts, no finish line yet),
`outline` (a structure you keep editing), `meeting` (notes from a
meeting, kept as a subject rather than a day), `draft` (text on its way
somewhere else), `other`. A `reference` note carries `source_url` and
`consumed`, `false` until the user has actually read or watched it;
`consumed` and `source_url` mean nothing on the other five kinds and
are left off there.

**`idea` exists because a Topic and a Project both refuse the job.** A
Topic is a quarterly exploration and you only run three at a time. A
Project is bounded work with a finish line. A video idea, a business idea,
a thing you want to build one day is neither: it has no finish line, and
it is not one of your three explorations. Before `idea` existed these were
filed as `outline`, which worked and told you nothing about whether the
idea was still alive.

An `idea` note carries `idea_status`, one of `open` (collecting thoughts),
`promoted` (it became a Project or a Topic; record which in
`projects` or `topics`), `parked` (still interesting, not now) or
`dropped` (decided against, kept so the decision is not re-litigated).
Default `open`. It is meaningful on `note_type: idea` only.

Ideas obey the link rule like every other note: at least one of
`projects`, `key_elements`, `topics`. A video idea anchors to the Key
Element it would serve. An idea that anchors to nothing failed the
Capturing Beast and should not be a note.

**`type: document`.** A scanned PDF or any other binary cannot carry
frontmatter, so the binary is never the metadata-bearing record. Every
document gets TWO files:

- the binary itself in `05 Assets/Documents/` (the shelf, per
  [[GL-1001-the-six-rooms|GL-1001]]);
- one markdown WRAPPER NOTE in `04 Inner World/Notes/`
  (`type: document`), holding all structured metadata in frontmatter
  and linking the binary via `source_file` (mandatory).

**The link rule.** Every `type: note` carries at least one of
`projects`, `key_elements`, `topics` (wikilink lists, the same value
shape `goal` and `key_element` already use), and may carry `people` and
`companies`. A note that links to none of the three failed the
Capturing Beast ([[GL-1007-capture-and-where-things-go|GL-1007]]) and
should not exist; `Scripts/validate-scaffold.py` fails a `type: note`
without one of the three. A `document` carries the same three lists as
optional fields, because a contract or an invoice is often filed for
the contact it belongs to and nothing else; `people`/`companies` carry
that.

`Notes.base` shows the `type: note` rows; `Documents.base`, in the same
folder, shows the wrapper notes, never the binaries. `preview_image`
points at a generated `.png` of the document's first page (in
`05 Assets/Images/`) and feeds the cards view; leave it off until a
preview exists, never fabricate. `amount`/`currency` are for invoices
and receipts; `issued_on` and `expiry_date` are ISO dates;
`people`/`companies` wikilink the contacts a document belongs to.
Generate wrapper notes deliberately, one document at a time, never as
a bulk backfill over thousands of files (a mass backfill is a known
Obsidian indexer killer).

## Meeting notes: bring your own transcriber (ruling 2026-09-11)

**The Scaffold does not record meetings and will not.** You already have a
transcriber you like, or your company does: Wispr Flow, Granola, Otter,
Fireflies, the built-in one in your call software. Building a worse one
inside Obsidian would have been a second-rate copy of a solved problem, and
it would have tied your meeting notes to our plugin.

What the Scaffold owns is the part no transcriber does: **turning an hour
of what was said into the few lines of what you now think.**

So a meeting produces two things, and they are not the same thing:

| | What it is | Where it lives |
| --- | --- | --- |
| **The transcript** | a machine record of what was said. You did not write it, so it is outer-world raw material | wherever your tool keeps it, or exported into `05 Assets/`, or dropped in `01 Inbox/Outer World/` |
| **The meeting note** | what you concluded, decided and noticed. Only you can write it | `04 Inner World/Notes/`, `note_type: meeting` |

The note is the record you keep and edit for weeks. The transcript is
material you consult and usually never open again.

```yaml
type: note
note_type: meeting
created: 2026-09-09
transcript: https://app.wisprflow.ai/notes/<id>
transcribed_by: Wispr Flow
ai_summary: claude-opus-5
audio_retained: false
projects: ["[[myICOR]]"]
people: ["[[Alex Rivera]]"]
```

- `transcript` is optional and meaningful on `note_type: meeting` and
  `other` only. It holds **one** of three shapes, whichever is true for
  you: a URL to the transcript in your tool, a quoted wikilink to a
  transcript file you exported into `05 Assets/`, or a quoted wikilink to a
  transcript note that came in through `01 Inbox/Outer World/`. One field,
  three shapes, because the point is that the Scaffold does not care which
  tool you use.
- `transcribed_by` is text, meaningful on `note_type: meeting` only. The
  tool that produced it, in the words you would say out loud:
  `Wispr Flow`, `Granola`, `Otter`, `whisper.cpp large-v3-turbo`. It is
  there so that in two years you can tell a transcript you trust from one
  you do not. Leave it off when there was no transcript.
- `ai_summary` is text, meaningful on `note_type: meeting` only. Absent or
  empty when the note carries no AI block. When an AI enriched the note
  from the transcript it holds the model id, for example `claude-opus-5`.
  Never a boolean, never a sentence: a reader has to be able to answer
  "which model wrote this" from the field alone.
- `audio_retained` is a boolean, meaningful on `note_type: meeting` only.
  `true` when you kept the audio somewhere you control, `false` when the
  audio is gone or lives only in a third-party tool. It exists because
  "can I still re-listen to this" is a question you will ask, and the
  answer is not derivable from anything else in the note.
- **Three fields, not a copy of the transcript.** Attendees, duration and
  what was said stay where they are. A second copy of a fact is a fact that
  drifts.

**Consent is yours, not ours.** The Scaffold never starts a recording, so
it never asks for consent on your behalf. Whatever your transcriber asks,
and whatever the law where you and the other people are, is between you and
them. A `transcript` field is a pointer, and pointing at a recording you
were not allowed to make does not become allowed because it is in a note.

- The link rule is unchanged: a meeting note still carries at least one of
  `projects`, `key_elements`, `topics`. When the member skips the link
  question at Stop, the plugin writes a quick capture in
  `00 Daily Scratchpad/` instead and no note is made, so no note is ever
  manufactured that `Scripts/validate-scaffold.py` must fail.

**Why those three break the no-copy rule.** Each answers a question asked
from outside the note, and a question you can only answer by opening a
JSON file in an asset folder is a question nobody answers. `audio_retained`
is the member's evidence for a GDPR Art. 13 retention question, and it has
to read true or false at a glance across every meeting note at once.
`ai_summary` is the EU AI Act Art. 50(2) marking obligation as data rather
than as prose, so a query can find every AI-written summary in the vault
and the visible label in the body has something to agree with. Holding the
model id rather than `true` costs nothing and answers the follow-up
question in the same breath. `transcribed_by` is "transcribed on device by
<model>" as a field, which is what makes "did anything leave this machine"
answerable without reading the package. Duration, consent and the recorded
times stay in the package alone, because nothing outside the note ever asks
them in bulk. Written for the 2026-09-09 legal ruling on the recorder so
the build does not invent these three field names itself.

## PDF highlights: one note per highlight (ruling 2026-09-07)

ICOR for Life - PDF Annotation writes one markdown note per highlight made
on a PDF in Obsidian's built-in viewer, `type: pdf-highlight`. The
wrapper-note pattern above holds one level down: the PDF is never changed
and never carries metadata; the highlight note does. The plugin owns the
frontmatter and the first lines of the body; everything under `## Note`
is the user's.

Home: `04 Inner World/Notes/Highlights/<pdf-basename>/<YYYY-MM-DD-HHMMSS>-p<page>-<4 chars of the id>.md`,
the plugin's default folder (a setting), one subfolder per PDF. The
scaffold ships the folder empty. A note may be renamed or moved: the
plugin finds highlights by their frontmatter, never by name or folder.

```yaml
type: pdf-highlight
highlight_id: k3f9x2mq7a1b               # 12 characters, made once, never re-derived
source_file: "[[05 Assets/Documents/paper.pdf]]"   # wikilink to the PDF
document: "[[paper]]"                    # optional: the type: document wrapper note for the PDF
page: 3                                  # 1-based
anchor: selection                        # selection (text) | rect (a drawn box)
selection: [16, 0, 18, 42]               # selection anchors only: core's own PDF link contract
rects: [[72, 640.2, 402.5, 654.9]]       # [x0, y0, x1, y1] in PDF user space; one per line of text, one box for rect
color: yellow                            # yellow | red | orange | green | blue | purple
quote: "the exact selected text"         # selection anchors; for rect, the text inside the box, or empty
image: "[[05 Assets/Images/paper-p3-k3f9x2mq7a1b.png]]"   # rect anchors only
created: 2026-09-07T10:15:00
canvases: ["[[Maps/Reading.canvas]]"]    # plugin-owned: the canvases the note is on
linked_notes: ["[[Notes/A]]"]            # plugin-owned: notes whose canvas cards connect to this one by an edge
cssclasses: [icor-pdf-highlight]
```

| Field | Value | Required |
| --- | --- | --- |
| `type` | `pdf-highlight` | yes |
| `highlight_id` | 12 character opaque id, made once, never re-derived | yes |
| `source_file` | wikilink to the PDF | yes |
| `document` | wikilink to the `type: document` wrapper note for the PDF | optional |
| `page` | 1-based integer | yes |
| `anchor` | `selection` or `rect` | yes |
| `selection` | `[beginIdx, beginOffset, endIdx, endOffset]`, core's own PDF link contract | selection anchors only |
| `rects` | list of `[x0, y0, x1, y1]` in PDF user space | yes |
| `color` | `yellow`, `red`, `orange`, `green`, `blue`, `purple` | yes |
| `quote` | the selected text | selection anchors |
| `image` | wikilink to the cropped PNG | rect anchors |
| `created` | ISO datetime | yes |
| `canvases` | list of wikilinks to `.canvas` files | plugin-owned |
| `linked_notes` | list of wikilinks to notes whose canvas cards connect to this highlight's card by an edge, either direction | plugin-owned |
| `cssclasses` | `[icor-pdf-highlight]` | yes |

- **Body shape.** `> quote ^quote` first, then `![[image]] ^image` for a
  rect anchor, then `## Note`. The two block ids are what a canvas card
  or an embed (`![[<note>#^quote]]`) points at; keep them.
- **Flat wikilink lists, never maps.** `canvases` and `linked_notes` are
  lists of wikilink strings. The graph, backlinks and Bases read a flat
  wikilink list, so a canvas edge becomes a visible edge in the vault; a
  list of maps is text to the Properties panel and invisible to everything
  else. `selection` is Obsidian's own contract (the four numbers the
  viewer's "Copy link to selection" writes), so a highlight opens in the
  built-in viewer without the plugin.
- **Wikilinks, not bare names.** Every link field carries the wikilink the
  plugin writes, so Obsidian follows a PDF or note rename. Nothing here is
  typed by hand: the plugin writes the frontmatter, and an agent that needs
  a highlight's facts reads them.
- **Not in `Documents.base`, and no `Highlights.base` yet.** `Documents.base`
  filters `note.type == "document"`, so highlights never crowd it. The
  plugin's sidebar answers "what did I highlight in this PDF"; a
  cross-PDF Base goes through `Scripts/new-base.py`'s registry
  ([[GL-1006-bases-and-live-views|GL-1006]]) once there is a corpus to read.

## People follow-up fields (ruling 2026-08-29)

- `last_contact` (ISO date): when the user last meaningfully touched
  base with this person. Updated by the team when a journal entry or
  processed capture shows a real interaction; never guessed.
- `next_action` (free text, short): the one next thing to do with
  this person ("send the proposal", "congratulate on the launch").
  Cleared when done, not archived; history lives in the Journal.

## The processed stamp (scratchpads, captures, document wrapper notes)

The stamp has exactly one shape:

```yaml
processed: true
processed_summary: "2 journal entries, 1 topic update"
processed_into:
  - "[[2026-08-27_some-entry]]"
  - "[[Some Topic]]"
```

`Scripts/stamp-processed.py` writes it and, for a text capture, moves
the capture to `01 Inbox/Outer World/archive/`. Without the scripts you
may type the same shape by hand: `processed` ticked, `processed_summary`
in one line, `processed_into` a list with at least one quoted wikilink;
then drag a capture into `Outer World/archive/` yourself, and leave a
scratchpad where it is. `Scripts/check-quality.py` verifies the shape
either way, so a stamp typed by hand and a stamp written by the script
are the same stamp, and a source without it counts as still waiting. The
body of the stamped note is never edited. A binary capture cannot carry
the stamp; its wrapper note does (next section).

## Binary captures and the processed stamp (ruling 2026-09-04)

A scanned PDF, a photo, an audio memo: a binary capture cannot carry
frontmatter, so it can never carry the processed stamp itself. Two
rules met on that case and gave different answers.
[[GL-1001-the-six-rooms|GL-1001]] keeps binaries in `05 Assets/`
forever; hard rule 2 of `AGENTS.md` keeps processed outer-world
originals in `01 Inbox/Outer World/archive/` forever. This ruling
breaks the tie:

- **The wrapper note carries the stamp.** The `type: document` note in
  `04 Inner World/Notes/` (the wrapper-note pattern above) is the
  metadata-bearing record, so `processed`, `processed_summary` and
  `processed_into` live there; the table declares them optional on
  `document`. A photo or an audio memo that needs a record gets the same
  wrapper with `doc_type: other`. No sidecar stamp note beside the
  binary: that would be a third file per document and a second place to
  look for one fact.
- **The move to the shelf IS the archive.** A binary capture is MOVED
  from `01 Inbox/` to its `05 Assets/` subfolder, never copied there.
  "Never deleted" is honoured by the move: the bytes survive, in their
  permanent room, linked from the wrapper note via `source_file`. A
  second copy in `Outer World/archive/` would duplicate the file and
  leave a binary sitting in `01 Inbox`, which GL-1001 exists to prevent.
- **The move is verified by code, not by care.**
  `Scripts/stamp-processed.py <wrapper-note> --capture <binary>` stamps
  the wrapper note and removes the inbox original only after the shelf
  copy (resolved from `source_file`) matches it byte for byte by
  sha256. A mismatch fails loudly and removes nothing.

Text captures are unchanged: the capture is its own note, carries the
stamp itself and moves to `Outer World/archive/` via `--archive`. No
capture is both shapes, and the script refuses `--archive` and
`--capture` together.

## Goals and Projects (ruling 2026-08-28)

- A goal tracks exactly two states: `not-achieved` and `achieved`.
  New goals start `not-achieved`; the flip to `achieved` is an event
  worth a journal entry.
- A project carries `start_date` (set at creation) and `end_date`
  (set when it closes), plus its lifecycle `status`.
- **No project can exist without a goal.** Every project's `goal`
  field holds a wikilink to the goal it serves. If the user starts a
  project and no fitting goal exists, the goal is created FIRST (one
  question, not a workshop). `Scripts/validate-scaffold.py` fails any
  project note without a goal link.

## Workstreams as goal carriers, and the standing WiP folders (ruling 2026-09-15)

A goal is carried by the work that moves it. Two shapes were taught: a
**Project**, bounded, with a finish line, and a **Habit**, a practice on a
cadence. The third shape is a **Workstream**: a repeatable process the
team runs again and again, producing one result per run and never
reaching a finish line. A video made every week carries a revenue goal;
no single video is the project, the process is the carrier. A Topic is
still never a carrier.

- `workstreams` on a `goal`: a wikilink list to the Workstream notes that
  carry it (`workstreams: ["[[WS-1002-weekly-review]]"]`). Name the hub
  Workstream every run passes through, not every stage. Optional; a goal
  carried by a Project alone carries no key.
- `workstreams` on a `project`: the Workstream(s) a bounded project runs
  through, same shape. Optional.
- `wip_folder` on a `workstream`: the standing working folder
  `03 WiP/Workstreams/<Name>/` where the team keeps the running state of
  the process (the queue, the current run, one dated subfolder per run).
  One string, set only when the folder exists. It is a field because it
  is not derivable: one folder may serve several Workstreams and the
  folder name is not the id.
- **The working folder of a Project is not a field.** It is
  `03 WiP/Projects/<Project note name>/`, derivable from the note, and a
  derivable fact is not a field (the same rule that keeps `week_start`
  off a planner week). The Project note carries a `## Working folder`
  line so a reader finds it without knowing the rule.
- The Workstream note does not mirror the goal back. It is an operational
  document, not a My Life entity, and the Goals room is where the carrier
  question is asked.

The four buckets of `03 WiP/`, the order they are read in, the two
standing trees among them and a worked example each: `03 WiP/README.md`
and the `README.md` in every bucket. `Scripts/checkpoint.py` never
proposes a bucket or a standing tree as a candidate to leave; `life-snapshot.py` reports the
Workstream carriers beside the Project and Habit ones
(`goals.open[].carriers.workstreams`).

## ICOR Journey reflections (ruling 2026-08-28)

Growth assignment reflections from the user's app.myicor.com account sync
into `04 Inner World/ICOR Journey Notes/`, one note per reflection, written
by the myICOR Connect plugin (code, per [[GL-1005-code-vs-instructions]]).

- `myicor_id` is the sync key. The sync is CREATE-ONLY: a note whose
  `myicor_id` already exists locally is never touched again, so the user
  may edit, extend, and wikilink these notes freely (original text stays
  sacred in both directions).
- The reflection answer is written verbatim into the body under
  `## My answer`. The plugin never rewrites it.
- `reflected_at` is the date the user answered in myICOR; `synced_at` is
  when the note landed in the vault.

## Planner items (ruling 2026-08-28)

Open tasks from external tools (Todoist, ClickUp, starred email) sync into
`02 Planner/<Source>/`, one note per item, written by the ICOR Planner
plugin (code, per [[GL-1005-code-vs-instructions]]). Google Calendar events
render on the board but never become notes.

- `type: planner-item`. `source` + `external_id` form the sync key; the
  upsert is idempotent against it, so re-syncing moves nothing and
  duplicates nothing.
- Source-owned fields (sync overwrites them): `title`, `due`, `priority`
  (normalized 1 highest .. 5 none), `url`, `tags`, `source_status`,
  `status` (`open`/`done`, reconciled from the source's full open set),
  `synced_at`, `done_at`.
- Plan-owned fields (sync never touches them; the board, the user, and
  the AI team write them): `planned_day` (`YYYY-MM-DD` or null),
  `planned_half` (`am`/`pm`/null), `planned_order` (fractional rank),
  `done_local` (the check; if the user armed "Complete on source" it also
  closes / reopens the task at the source),
  `weekly_goal` (pins to the top of the tray).
- Moving an item on the plan IS editing `planned_day`/`planned_half`/
  `planned_order`; the board re-renders live. This is the sanctioned way
  for agents to plan work for the user.
- These notes are machine-tended: never rename or move them by hand.
  With "Push edits to source" on (the default), editing the note BODY or
  `due` / `priority` syncs back to Todoist / ClickUp on the next detection,
  so body edits are sanctioned and travel.
- Recurring tasks (Planner 0.7.3), all source-owned: `recurring` is
  `true`, `false`, or `null` when the source cannot say (ClickUp, or a note
  from before the field existed); `due_string` is the source's own
  recurrence phrase ("every monday"), Todoist only; `last_completed_due` is
  the due date of the most recently finished occurrence; `occurrences`
  lists finished occurrences oldest first, at most 30, each with `due`,
  `planned_day`, `planned_half`, `done_at`. `reopen_pending` is `true`
  between unchecking a source-closed card and the source confirming the
  reopen: the board sets it, sync clears it, and reconcile stands down
  while it is set.
- Subtasks: `parent_id` is the source's id of the parent task as a string,
  or `null`. Source-owned. It resolves inside the same `source` only; a
  child whose parent is not in the vault is an ordinary item.
- Manual items carry `created_at` in place of `synced_at`.

## Planner routines (ruling 2026-09-04)

A routine is a fixed block of the day (morning, afternoon or evening) with
a short checklist of steps. Routines are a Planner concept, not a My Life
entity: they live in `02 Planner/Routines/`, one note per routine, and the
Planner plugin creates the folder when it needs it. The frontmatter is the
definition; the body holds the steps and the log.

```yaml
type: planner-routine
name: Morning launch
routine_type: morning                 # morning | afternoon | evening
start: "06:30"                        # HH:MM, local time
end: "07:30"                          # HH:MM, must be after start
weekdays: [mon, tue, wed, thu, fri]   # same lowercase 3-letter codes as cadence_days
active: true
created_at: 2026-09-04T09:00:00Z      # optional
```

Body, two fixed sections:

```markdown
## Steps
- [ ] Water, 500 ml
- [ ] One journal page
- [ ] Plan the day on the board

## Log
<!-- routine-log: schema=steps -->
| Date | Done | Steps |
|---|---|---|
| 2026-09-04 | 3/3 | 1,2,3 |
| 2026-09-03 | 1/3 | 2 |
| 2026-09-02 | S | |
```

- `## Steps` is the definition. The plugin never writes its boxes and reads
  them as labels only; a `- [x]` there counts as unchecked, because the
  day's state lives in the log. Steps are identified by position (1-based),
  so editing the list mid-day changes that day's mapping; the log keeps the
  count that matters.
- `## Log` carries the `<!-- routine-log: schema=steps -->` sentinel on its
  own line immediately before the table. Columns are `Date | Done | Steps`:
  `Date` is an ISO date, `Done` is `n/m` (steps done of steps defined) or
  `S` when the routine was skipped that day, `Steps` is the comma-separated
  positions that were done. One row per date. Newest on top is the
  default; a writer keeps whatever direction the table already has and
  replaces a day's row in place, never rewriting the lines around it.
- An agent answers "what is the morning routine and was it done today" by
  reading the steps from `## Steps` and today's row from `## Log`. An agent
  may append a row in chat, the same way it does for a habit.
- Never a streak, a count or a done-state in frontmatter. Definition in
  frontmatter, log in the body: the same rule as Habits below.

## Habits: the meaning note and the planner note (ruling 2026-09-06, supersedes 2026-09-04)

The 2026-09-04 ruling put `cadence`, `cadence_days`, `started_on` and the
daily log on the My Life habit note itself. The Planner plugin now owns
habit tracking as its own entity, the same way it already owns Routines,
and this ruling splits the two apart for one reason: two notes writing the
same fact is not SSOT. A habit's SCHEDULE and its LOG belong to whichever
surface the Planner renders and checks off; a habit's MEANING (why it
matters, what it looks like, the reflection) belongs to My Life. A field
lives in exactly one of the two notes, never both.

**The My Life habit note (`04 Inner World/My Life/Habits/`, one flat `.md`
per habit) keeps only meaning.** `cadence`, `cadence_days` and
`started_on` are removed from the `habit` type entirely, not kept as an
optional hint: a schedule hint that can drift from the real, Planner-held
schedule is worse than no hint, and the Planner note is one wikilink away
via `planner_habit`.

```yaml
type: habit
name: Morning walk                # optional; the filename is the name when absent
status: active                    # active | paused | abandoned
planner_habit: "[[02 Planner/Habits/Morning walk]]"   # optional, full path
tags: []
```

- `status` here is whether the user still holds this as a life practice
  at all (`active`/`paused`/`abandoned`); it is independent of the
  Planner's own `status` on the tracking note below, so a habit can read
  `abandoned` here while its planner-habit note still shows `active` for
  a day or two until tracking is turned off too.
- `planner_habit` is optional and points forward to the tracking note.
  **It carries the full vault path, never a bare `[[Morning walk]]`**: the
  two notes share a name by design, one in `02 Planner/Habits/` and one in
  `04 Inner World/My Life/Habits/`, so a bare link cannot say which of the
  two it means and Obsidian resolves it by proximity rather than by intent
  (ruling 2026-09-16). The same rule holds for `linked_note` pointing back.
  Ruling: this is not a violation of a one-way-linking rule, because this
  scaffold states none; [[SOP-1004-create-or-update-a-my-life-entity|SOP-1004]]
  step 7 already directs agents to cross-link both directions wherever the
  schema carries fields for it (person and key element, goal and key
  element), so a habit and its planner-habit note follow the existing
  norm rather than break it. When the field is absent (a habit created
  before an import, or a vault that has not imported Habit tracking yet),
  the planner note is still found by searching `linked_note` for this
  note's wikilink; no agent should read a missing `planner_habit` as "not
  tracked."
- Body sections stay `## Why this habit`, `## What it looks like`,
  `## Reflection`. There is no `## Daily log` here any more: the log
  moved to the planner-habit note below.

## Planner habits: cadence, status and the log (ruling 2026-09-06)

A tracked habit is a Planner concept now, the same shape of decision as a
Routine: it lives in `02 Planner/Habits/`, one note per habit, and the
Planner plugin creates the folder when it needs it. The frontmatter is
the schedule; the body holds the log.

```yaml
type: planner-habit
name: Morning walk
cadence: daily                      # daily | weekdays | weekly | monthly
cadence_days: [sun, wed]            # optional, weekly cadence: mon..sun codes
month_day: 15                       # optional, monthly cadence: 1..28
status: active                      # active | paused | archived
started_on: 2026-04-01              # optional, ISO date
linked_note: "[[04 Inner World/My Life/Habits/Morning walk]]"  # optional, full path
created_at: 2026-09-06T09:00:00Z    # optional, ISO datetime
tags: []
```

- `cadence` is the rhythm the Planner schedules the habit on: `daily`,
  `weekdays` (Monday to Friday), `weekly` or `monthly`. `weekly` pairs
  with `cadence_days` when the habit lands on named days rather than
  every day ("twice a week, Sunday and Wednesday" is `cadence: weekly`
  plus `cadence_days: [sun, wed]`, lowercase 3-letter day codes);
  `monthly` pairs with `month_day`, capped at 1 to 28 so every month can
  honour it without a 29/30/31 edge case.
- `status` is the Planner's own tracking state (`active`/`paused`/
  `archived`), a different value set from the meaning note's `status`
  above on purpose: archiving here stops the habit from rendering on the
  board; it does not touch the My Life note or its own `status`.
- `started_on` is the ISO date tracking began. `linked_note` is the
  FULL-PATH wikilink back to the My Life habit note when the Habits room is
  also in use, `[[04 Inner World/My Life/Habits/Morning walk]]`, for the
  same reason `planner_habit` is qualified above: the two notes share a
  name by design and a bare link cannot say which one it means. A
  Planner-only habit (no meaning note yet) leaves it off.
  `created_at` is this note's own creation timestamp.
- **The import writes a `planner-habit` note FROM an existing My Life
  habit note.** It moves `cadence`, `cadence_days` and `started_on` off
  the My Life note and onto this one, moves the `## Log` table with them,
  and sets `linked_note` to the My Life note it came from. Nothing is
  copied and left behind: the source fields and the log are removed from
  the My Life note in the same operation, per the "field lives in exactly
  one note" rule above. A vault that has not run the import yet keeps
  running on the pre-2026-09-06 shape until it does; nothing breaks by
  standing still.

### The log: the `<!-- habit-log: schema=... -->` sentinel

The daily log lives here now, not on the My Life note, as a markdown
table in the body (human-readable, editable in chat or by hand,
canonical). So that code can parse the table deterministically, place a
single HTML-comment sentinel on its own line immediately before the
table, under a `## Log` heading (matching the Routine's `## Log`):

```markdown
## Log
<!-- habit-log: schema=streak -->
| Date | Y/N | Note |
|---|---|---|
| 2026-09-06 | Y | |
| 2026-09-05 | N | slept in |
```

The sentinel is invisible in Obsidian and unambiguous for the parser.
Two schemas cover the known patterns:

- `schema=streak`: the first column is a date and the second a binary
  done marker; any further columns are folded into a note. Used by
  streak-style and green/red trackers.
- `schema=process`: the same two columns plus a third column captured as
  the trigger (what set the habit off, or what drifted). Used by process
  trackers that have no streak by design.

Markers, both schemas:

| marker | meaning |
| --- | --- |
| `Y`, `✓`, `G` | done |
| `N`, `R`, an en dash (U+2013) | not done |
| `_`, an em dash (U+2014), blank | pending: the day is not over |

One row per date. Newest on top is the default; a writer keeps whatever
direction the table already has and replaces a day's row in place, never
rewriting the lines around it. Streaks are never written into the table or
the frontmatter; they are computed from the rows at read time, which is
what stops self-reported streaks from drifting. The Planner's check-in
writes exactly this: `Y` on check, `_` on uncheck (or `N` when the row
already carries a note), and it creates the `## Log` section with the
`streak` sentinel when the note has none.

## Planner weeks: weekly priorities and the daily highlight (ruling 2026-09-15)

One note per ISO week, `02 Planner/Weeks/YYYY-Www.md`, `type: planner-week`.
It is the home of two things ICOR had no place for: the **Weekly
Priorities** and the **Daily Highlight**. Same shape of decision as a
Routine and a Habit: the frontmatter is the definition, the body holds
the content behind a sentinel, and the Planner plugin can grow a Week
view over it later without a migration.

> The Daily Highlight is the one thing that, if it happens, makes the
> day a win: chosen in the morning, confirmed in the evening.

### The ladder, and why the day was the missing rung

| Rung | Span | Home | The ICOR name |
| --- | --- | --- | --- |
| Key Element | permanent | My Life | Key Element |
| Goal | until achieved | My Life | Goal |
| Project, Habit or Workstream | bounded, cadenced, or repeating without end | My Life for the meaning, Planner for the tracking, `06 AI Team/AI Team Knowledge/Workstreams/` for the process | the carriers |
| the week | one ISO week | this note | **Weekly Priority** |
| the day | one calendar day | this note | **Daily Highlight** |

### The two labels, and the one word that does not move

**"Goal" belongs to a `type: goal` note in `04 Inner World/My Life/Goals/`
and only there.** A Goal is the measurable commitment anchored to a Key
Element and carried by a Project, a Habit or a Workstream. That is the
taught meaning and it does not move.

| Label | What it names | Where it is said |
| --- | --- | --- |
| **Goal** | a `type: goal` note | chat, `Goals.base`, the My Life INDEX, the course |
| **Weekly Priority** | one line in this week's note: an outcome for the week, with a done state | chat, the heading here, the Planner tray, `life-snapshot.py --brief` |

**The starred planner item is neither.** It is a task **pinned to the
week**: `weekly_goal: true` on a `planner-item` keeps its key for now,
and stops wearing the word "goal" on every surface (tray section
**PINNED THIS WEEK**, chip **WEEK**). A task may serve a Weekly
Priority; the priority is the outcome, the task is the means. The
item-level `priority` (1 to 5, source-owned) never appears with the word
"weekly" beside it, so the two never meet.

### The note

```yaml
type: planner-week
week: 2026-W38                        # required, ISO week, matches the filename
created_at: 2026-09-14T07:00:00Z      # optional
tags: []
```

No `week_start` and no `week_end`: both derive from `week`, and a
derivable fact is not a field. Nothing computed goes in the
frontmatter either: no done count, no streak, no "priorities this week:
3", for the same reason a habit streak is never written into its log.

```markdown
## Weekly priorities
<!-- weekly-priorities: schema=checklist -->
- [ ] Ship the explainer video
- [x] Book the sleep lab follow-up

## Daily highlights
<!-- daily-highlights: schema=highlight -->
| Date | Highlight | Done |
|---|---|---|
| 2026-09-15 | Record episode 3 | _ |
| 2026-09-14 | Paco review call | Y |
```

- `## Weekly priorities` carries `<!-- weekly-priorities: schema=checklist -->`
  on its own line immediately before the list. One priority per `- [ ]`
  line; `- [x]` is done. Order is yours and nothing sorts it. A line that
  is not a checkbox is not a priority: the parser ignores it and every
  writer leaves it exactly where it is.
- `## Daily highlights` carries `<!-- daily-highlights: schema=highlight -->`
  immediately before the table. Columns `Date | Highlight | Done`:
  `Date` is an ISO date inside the week, `Highlight` is one sentence,
  `Done` uses the marker set the habit log already defines (`Y` done,
  `N` not done, `_` or blank pending). One row per date, newest on top,
  and a writer replaces a day's row in place rather than rewriting the
  lines around it.

### The four rules the concept carries

1. **One sentence, one per day.** Not a list and not a task. A Planner
   item may serve it; the highlight is the outcome, the item is the
   means. It may carry a wikilink to a Project, Key Element or Topic,
   and `life-snapshot.py` counts that as attention for the linked note.
2. **One sense, two moments.** The morning sets the sentence, the
   evening confirms it. "What turned out best today", judged
   afterwards, is a different thing and already has a home: a
   `journal_type: milestone` entry. **The model never writes a sentence
   into this table from a guess.** On a day with no morning sentence it
   may offer one drawn from today's entries, and only your confirmed
   words land.
3. **A blank day is not a finding.** No highlight set means one line
   saying so. Nothing nags.
4. **Planner-owned.** Never a daily-note property (the daily note is
   blank by design, per [[GL-1007-capture-and-where-things-go|GL-1007]])
   and never a journal field.

Never bare "Highlight" as a label, a heading or a sentinel: in this
scaffold `highlight` already means a PDF highlight (`type: pdf-highlight`).
The day sense always carries the word **Daily**; the PDF sense always
carries **PDF** in prose. Neither side changes a filename or a type.

### Who writes it

`Scripts/planner-week.py` creates and edits the note:
`ensure` (this week's note, both sections empty, refuses to overwrite),
`add-priority`, `done-priority`, `set-highlight`, `mark-highlight`.
Filing is deterministic, so the team runs the script rather than editing
the table by hand ([[GL-1005-code-vs-instructions|GL-1005]]). Editing
the note yourself in Obsidian is equal: the parser reads the shape, not
the writer. `life-snapshot.py` only ever reads it.
