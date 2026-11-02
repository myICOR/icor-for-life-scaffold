# Scripts

The deterministic half of the work on your rooms: the life scripts ICOR for
Life ships. Anything a machine can tell you got wrong lives here as code;
anything only judgement can answer stays as prose in the Guidelines
([[GL-1005-code-vs-instructions|GL-1005]]).

The AI team's own scripts (the hooks and guards, the harness generator, the
updater, the task, session and hire tools, and the red-test suite) are not
part of ICOR for Life. They ship with myPKA, and their reference is
`README-myPKA.md` in this same folder once myPKA is in it (mode A), or in the
myPKA folder (mode B).

You never need to open this folder. Describe a rule in plain words and the
AI writes and maintains the script; these pages are the reference for the
AI, and for anyone who wants to run a check by hand.

Every script prints `OK ...` and exits 0 when it is happy, and `FAIL ...`
with exit 1 when it is not. The fixture suites beside them
(`test-life-snapshot.py`, `test-link-dates-to-daily-notes.py`,
`test-note-scripts.py`, `test-build-scaffold-manifest.py`) feed each one
what it must reject, and myPKA's `run-red-tests.py` runs on a folder that
holds both products.

## The scripts

| Script | What it does | Typical call |
| --- | --- | --- |
| `build-release-zip.sh` | Builds the distribution zip, with no personal data, no tokens, and no version that disagrees with the bytes | `build-release-zip.sh` |
| `build-scaffold-manifest.py` | Builds `.icor-for-life/manifest.json`, the machine-readable description of a release that Scaffold Check compares a vault against | `build-scaffold-manifest.py` |
| `test-build-scaffold-manifest.py` | The fixture suite behind the manifest's `previous_removed` map: every older state of a removed file is listed, nothing for a file that never changed, moved to myPKA or still ships | `test-build-scaffold-manifest.py` |
| `check-bases.py` | Checks every `.base` file: valid shape, columns that GL-1002 declares, one Base per collection | `check-bases.py` |
| `check-quality.py` | Measures the quality of what is in the vault: links, enums, required and invented fields, orphans, dangling links, the queues that are backing up | `check-quality.py --write` |
| `find-entity.py` | Finds the entity note a name or an alias belongs to, so one thing never gets two notes | `find-entity.py "Alex Rivera"` |
| `life-snapshot.py` | Answers the six everyday life questions from one regenerated file: goals, the projects to focus on, this week's priorities, today's highlight, key elements, the topics with recent attention | `life-snapshot.py --write --brief` |
| `test-life-snapshot.py` | The fixture suite behind `life-snapshot.py`: one case per rule, and the negative controls (a session log, an mtime and a double-counted scratchpad must all score 0) | `test-life-snapshot.py` |
| `link-dates-to-daily-notes.py` | Turns a full date written in a note body into `[[YYYY-MM-DD]]`, and creates the daily note it points at, so the backlinks alone make a blank daily note the timeline of that day (GL-1011) | `link-dates-to-daily-notes.py --fix` |
| `planner-week.py` | Creates and edits this week's Planner note: the weekly priorities checklist and the daily highlight table. It writes; `life-snapshot.py` reads. It never proposes a priority and never picks a highlight | `planner-week.py ensure`, then `planner-week.py add-priority "..."` |
| `set-property.py` | Sets or removes ONE frontmatter property on ONE note, refusing anything outside the field's closed set or outside GL-1002. The setter behind `focus_rank` | `set-property.py "<note>" focus_rank 1` |
| `new-base.py` | Stamps a house-shaped `.base` for one entity collection; also the one parser of GL-1002's per-type table that every other script reads | `new-base.py note` |
| `new-entity.py` | Creates one entity note from its template, in its room, already linked and with its required fields filled | `new-entity.py note "Title" --link "[[Health]]" --set note_type=outline` |
| `new-journal-entry.py` | Creates a journal entry in `YYYY/MM/` with the right name, and the user's words verbatim under `## Original Text` | `new-journal-entry.py --date ... --slug ... --journal-type thought --original "..."` |
| `open-in-obsidian.py` | Opens a vault file in Obsidian, in a new tab (the guided tour and the diagram rule use it) | `open-in-obsidian.py "<vault relative path>"` |
| `test-link-dates-to-daily-notes.py` | The fixture suite behind `link-dates-to-daily-notes.py`: one case per rule it claims, every IGNORE case a date it must not touch | `test-link-dates-to-daily-notes.py` |
| `test-note-scripts.py` | The fixture suite behind the scripts that write a note's frontmatter and the reader that judges it: wikilink values, dates in names, `concept:` captures, inline comments, frontmatter arrays | `test-note-scripts.py` |
| `stamp-processed.py` | Stamps a scratchpad, a capture or a document wrapper note as processed, and moves the original where it belongs | `stamp-processed.py <note> --summary "..." --into "[[x]]"` |
| `validate-scaffold.py` | Validates the structure: the rooms, the names, the date nesting, the file-tree styling, the templates and the property types | `validate-scaffold.py` |
| `noteio-icor.py` | A byte-identical copy of myPKA's `noteio.py`, pinned by sha256 in the manifest's `vendored` list: the life scripts read and write a note through it without rewriting a byte they never meant to touch. A fix lands in myPKA and comes back in the next release | (the life scripts import it) |

Two checks, two questions, on purpose: `validate-scaffold.py` answers "is
this a scaffold", `check-quality.py` answers "is what is in it any good".
A structure failure stops a release; a quality finding is a conversation
with you ([[SOP-1014-check-and-repair-what-was-filed-by-hand|SOP-1014]]).

## GL-1002 is parsed once

`new-base.py` is the only place that reads GL-1002's per-type table, and
it exposes three answers that the other scripts import rather than
restate:

- `gl002_fields(root)` -> `{type: every field the guideline declares}`,
  which answers "is this field invented".
- `gl002_required(root)` -> `{type: the required fields only}`.
- `gl002_enums(root)` -> `{type: {field: allowed values}}`, read from the
  `field (a/b/c)` shape beside the field name.

The table is read BY HEADER NAME, never by column position, so a new
column (the `template` column, added 2026-09-09) can never shift the
parse. It did once, and the cost was every shipped `.base` file reported
as carrying a column GL-1002 does not declare.

## quality.json

`check-quality.py --write` writes
`.icor-for-life/scripts/quality.json`, in the machine layer
([[GL-1008-the-machine-layer|GL-1008]]). The ICOR for Life - Scaffold
Check plugin reads it and renders the dashboard; Larry reads it at session
start and reports vault health in one line. It is regenerated, never
edited, and never tracked in git.

The shape is versioned by the top-level `schema` integer. **Inside a
schema version the metric ids, their order and every field name are a
contract**: a reader may rely on them. A change to any of them is a new
schema number.

```json
{
  "schema": 1,
  "generated": "2026-09-09T08:30:00Z",
  "scaffold_version": "1.17.0",
  "health": "ok | attention | broken",
  "counts": { "journal": 412, "notes": 96, "documents": 31, "people": 58,
              "companies": 14, "projects": 9, "goals": 4, "habits": 6,
              "topics": 22, "key_elements": 11, "scratchpads": 3, "inbox": 2 },
  "metrics": [
    { "id": "notes_missing_link", "label": "Notes without a link",
      "value": 7, "unit": "notes", "severity": "attention",
      "threshold": { "attention": 1, "broken": 50 }, "sop": "SOP-1014" }
  ],
  "findings": [
    { "metric": "notes_missing_link", "severity": "attention",
      "path": "04 Inner World/Notes/coffee-grinder-comparison.md",
      "message": "The note links to nothing in the vault.",
      "action": "Add one wikilink in projects / key_elements / topics to the thing it belongs to." }
  ]
}
```

| Field | Meaning |
| --- | --- |
| `schema` | the shape version, currently `1`. Check it before trusting a field |
| `generated` | when the report was made, ISO 8601 in UTC |
| `scaffold_version` | `.icor-for-life/VERSION`, or `unknown` in a vault that has none |
| `health` | the worst severity of any metric: `ok`, `attention` or `broken` |
| `counts` | how much of each kind of thing the vault holds; the denominator behind every metric |
| `metrics` | one entry per metric, always all of them, always in the order below |
| `metrics[].id` | the stable id; the only field a reader should match on |
| `metrics[].label` | the human name, for a heading |
| `metrics[].value` | the measurement |
| `metrics[].unit` | what the value counts: `notes`, `fields`, `links`, `days`, `pairs` |
| `metrics[].severity` | `ok`, `attention` or `broken`, from the thresholds below |
| `metrics[].threshold` | the two values the severity came from, so a reader can show "7 of 50" |
| `metrics[].sop` | the procedure that repairs this metric: `SOP-1014` |
| `findings` | the individual problems, worst first, at most 200. A finding under a metric that is still `ok` is left out: it is true, but there is nothing to do about it yet |
| `findings[].metric` | the metric id this belongs to |
| `findings[].severity` | that metric's severity (the worse of a paired queue) |
| `findings[].path` | vault-relative path of the note |
| `findings[].message` | what is wrong, one sentence |
| `findings[].action` | what to do about it, one sentence |

The thirteen metrics, in their fixed order:

| id | measures |
| --- | --- |
| `notes_missing_link` | notes filed under no Project, Key Element or Topic, and projects with no goal |
| `enum_violations` | a value outside a closed set GL-1002 states (`note_type`, `journal_type`, `doc_type`, `status`) |
| `missing_required_fields` | a field GL-1002 marks required for that type, absent or empty |
| `invented_fields` | a frontmatter key GL-1002 does not declare for that type |
| `orphans` | an entity or note nothing in the vault links to (`example` notes excluded) |
| `dangling_links` | a `[[wikilink]]` pointing at a file that does not exist |
| `documents_without_file` | a `type: document` note with no `source_file`, or one whose file is gone |
| `unprocessed_scratchpads` | scratchpads with no processed stamp |
| `unprocessed_scratchpad_oldest_days` | how long the oldest of them has waited |
| `unprocessed_captures` | anything still sitting in `01 Inbox/` |
| `unprocessed_capture_oldest_days` | how long the oldest of them has waited |
| `unconsumed_references` | `note_type: reference` notes not yet read or watched |
| `duplicate_entities` | two notes in one entity folder that name the same thing |

The thresholds are judgement, not doctrine: they live in one dict at the
top of `check-quality.py`, one comment per line, and are yours to move.

## snapshot.json

`life-snapshot.py --write` writes
`.icor-for-life/scripts/snapshot.json`, in the machine layer
([[GL-1008-the-machine-layer|GL-1008]]), beside `quality.json`. The AI
Team reads it at the start of a session and answers the six everyday
questions from it, with no folder walk: your goals, the projects to focus
on, this week's priorities, today's highlight, your key elements, and the
topics with your recent attention. It is regenerated, never edited, and
never tracked in git.

The shape is versioned by the top-level `schema` integer. **Inside a
schema version the field names and their order are a contract**: a reader
may rely on them. Renaming, removing, retyping or reordering any of them
is a new schema number. Adding a key is additive and stays inside the
version, dated here so a reader knows what an older writer will not
emit: `goals.open[].carriers.workstreams` (2026-09-15, the Workstream
carrier of GL-1002).

```json
{
  "schema": 1,
  "generated_at": "2026-09-15T15:32:00Z",
  "generated_local_date": "2026-09-15",
  "scaffold_version": "1.24.0",
  "week": { "iso": "2026-W38", "start": "2026-09-14", "end": "2026-09-20",
            "note": "02 Planner/Weeks/2026-W38.md" },
  "thresholds": { "topics_shown": 5, "attention_hot_score": 6, "focus_max": 3,
                  "weekly_goals_max": 5, "stale_after_hours": 6 },
  "goals": { "open": [], "achieved_90d": [],
             "order_rule": "target_date ascending, nulls last, then name" },
  "projects": { "focus": [], "active": [], "active_count": 2, "order_rule": "..." },
  "weekly_goals": { "week": "2026-W38", "path": null, "items": [],
                    "done_count": 0, "reason": "no note at ..." },
  "highlight": { "date": "2026-09-15", "text": null, "done": null,
                 "path": null, "reason": "no note at ...", "recent": [] },
  "key_elements": [],
  "topics": { "hot": [], "ranked_count": 1,
              "sources_counted": { "journal": 1, "scratchpad": 0,
                                   "notes": 1, "planner": 0 },
              "order_rule": "score desc, n7 desc, name" },
  "today": { "date": "2026-09-15", "journal_entries": [], "scratchpads": [] },
  "findings": [],
  "degraded": []
}
```

| Field | Meaning |
| --- | --- |
| `schema` | the shape version, currently `1`. Check it before trusting a field |
| `generated_at` | when the snapshot was made, ISO 8601 in UTC |
| `generated_local_date` | the local calendar date the run belongs to; staleness is judged on both |
| `scaffold_version` | `.icor-for-life/VERSION`, or `unknown` in a vault that has none |
| `week` | the ISO week the run used; `note` is the weekly Planner note, or null when there is none |
| `thresholds` | the dict the run used, so a reader can say what "hot" meant without opening the script |
| `goals.open[]` | every open goal, never trimmed; `carriers` holds the projects, habits and workstreams that carry it (`workstreams` since 2026-09-15; always present, empty when none) |
| `goals.achieved_90d[]` | empty until a dated completion exists; never guessed |
| `projects.focus[]` | ONLY projects carrying `focus_rank`; an empty list means no decision is recorded |
| `projects.active[]` | every open project with its activity facts, in `order_rule` order |
| `weekly_goals` | the checklist in this week's Planner note; `reason` says why it is empty |
| `highlight` | today's row; `done` is `true`, `false` or `null` (pending); `recent` holds the last seven rows |
| `key_elements[]` | every non-archived Key Element, ordered by attention score then name |
| `topics.hot[]` | the top `topics_shown` topics scoring above 0; `ranked_count` is how many were scored |
| `today` | the paths the AI needs for the one judgement question, so it never searches for them |
| `findings[]` | data-quality facts worth acting on: `goal_overdue_active`, `focus_over_max`, `focus_duplicate_rank`, `focus_rank_not_active`, `weekly_goals_over_max`, `journal_undated` |
| `degraded[]` | which input was missing and what that emptied; an empty list means every source was present |

`degraded` is "a missing report is never a green" turned inward. An empty
`goals.open` with `degraded` empty means you have no open goals; an empty
`goals.open` with a `degraded` entry naming the Goals room means the
script could not look. A reader has to tell those two apart, and this
field is what makes that possible.

The attention score counts one dated link event per source note, so a
journal entry that names a topic four times is one event. Events are
weighted 3 in the last 7 days, 2 for 8 to 14 days, 1 for 15 to 30, and
nothing older counts. `n7`, `n14`, `n30` and `last_seen` sit beside the
score, so you can always see why a number is what it is. File mtime and
the AI Team's own session logs are deliberately NOT signals: mtime moves
when a script rewrites frontmatter or a sync lands on a second device,
and a session log is the team's work record, not your attention.

### Readers of `snapshot.json`

The file is written by a script and read by a hook, a skill prerun and a
plugin, so the contract has two halves and this is the reader's half
(Vex F4, 2026-09-15). Every reader implements all five lines:

1. Refuse the file if it is larger than 2 MB, or is not a JSON object
   carrying `"schema": 1`.
2. Treat every string as untrusted display text. Never eval it, never
   build a shell command from it, never hand it to a wikilink resolver
   that opens files. The writer copies `key_element`, `carriers`, goal
   names and checklist lines verbatim out of frontmatter, so a note can
   put any string there.
3. A `path` or `note` value is opened only if it is relative, contains no
   `..`, and resolves under the vault root. Otherwise it is shown as text.
4. Apply the staleness rule: a stale or unparsable `generated_at` is
   reported as stale, never shown as current. An absent file means "the
   script did not run", never "you have no goals".
5. Cap what is injected into model context to the `--brief` shape, not the
   whole file.

The writer's own side: the payload is scanned against the same credential
pattern list `write-guard.py` uses, and a hit refuses the whole snapshot
rather than writing a redacted one; the write stays inside
`.icor-for-life/scripts/` whatever symlink is planted on the path; and
`scaffold_version` is validated against a version shape rather than
copied out of `VERSION` verbatim.

Thresholds are judgement, not doctrine: they live in one dict at the top
of `life-snapshot.py`, one comment per line, and are yours to move.
