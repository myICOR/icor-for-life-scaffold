---
name: capture
description: Decide where something the person wants to keep belongs in their ICOR for Life folder, and put it there. Use when they say "save this", "note that", "where does this go?", paste a thought, a link or a fact, or hand you a file.
---
# Capture: put it where it will be found

Run from the folder's root. The structure is in `_System/schema.json`; read it when you need a type's fields.

## 1. Connect first (the Capturing Beast)

Ask, in this order, and stop at the first yes:
1. Does it serve a current **Project**? (`02 My Life/Projects/`)
2. Does it touch a **Key Element** of their life? (`My Life/Key Elements/`)
3. Does it belong to one of their **Topics**? (`My Life/Topics/`)
4. Is it about a **person** or **company**? (`05 Contacts/`)

Find the existing note before you link: `python3 _System/Tools/find-entity.py "<name>"`. Never make a second note for the same thing. No yes at all: tell the person it connects to nothing yet, and offer to leave it in today's scratchpad or let it go.

## 2. Pick the home

| What it is | Home | How |
| --- | --- | --- |
| their words with a date as identity (what happened, what they thought) | `03 Journal/` | skill **write-journal-entry** |
| their knowledge with a subject that keeps changing (outline, meeting notes, idea, draft) | `04 Notes/` | `python3 _System/Tools/new-entity.py note "<Title>" --set note_type=<idea|outline|meeting|draft|other> --link "[[<Project/Key Element/Topic>]]"` |
| a fact about a person or company (phone, job, birthday) | their note in `05 Contacts/` | `python3 _System/Tools/set-property.py "05 Contacts/People/<Name>.md" <field> "<value>"` (fields: see schema `person`) |
| a file to keep | file in `10 Files/Documents/`, a `document` note | skill **new-object**, type `document` |
| a new goal, project, topic, habit, Key Element, person, company | `02 My Life/` or `05 Contacts/` | skill **new-object** |
| someone else's work (a book, an article, a video, a podcast, a post) | a `source` in `06 Sources/` | `python3 _System/Tools/new-entity.py source "<Title>" --set source_type=<book|article|video|podcast|post|paper|other> --set source_url=<url> --link "[[<Project/Key Element/Topic>]]"` |
| work not done yet: a draft in several files, a sketch, research for a decision | a dated folder in `08 Workbench/` | make `08 Workbench/<YYYY-MM-DD> <name>/brief.md` (what it is, the My Life item it serves as a link, the next step); anything else goes in beside it |
| you are not sure, or the person is busy | today's scratchpad, `00 Daily Notes/YYYY/MM/YYYY-MM-DD.md` | append one line; it can be carried on later, or stay |

Date or subject? Date: Journal. Subject: Notes.

A file goes in its folder, never in the top folder: pictures, screenshots and videos in `10 Files/Images/`, recordings in `10 Files/Audio/`, PDFs and office files in `10 Files/Documents/`, a scan to file later in `01 Inbox/Scanner Inbox/`. Nothing sorted yet: `01 Inbox/`. Never make a new folder next to the numbered folders.

## 3. Tell the person

One line: what you created or changed, where, and what it links to, as a `[[wikilink]]`.
