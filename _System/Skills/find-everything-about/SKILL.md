---
name: find-everything-about
description: Gather everything the ICOR for Life folder holds about one person, project, goal, topic or Key Element by following its links - journal entries, notes, contacts, related My Life items - and summarise it. Use when the person asks "what do I have about…", "show me everything on…", "remind me about Alex".
---
# Find everything about one thing

1. **Find the note**: `python3 _System/Tools/find-entity.py "<name>"` (it knows aliases). Not found: search titles and text, and ask.
2. **Read its own properties** (its type's fields in `_System/schema.json`).
3. **Follow the links both ways**:
   - out: the wikilinks in its frontmatter (`goal`, `key_elements`, `people`, `topics`…)
   - in: every note whose frontmatter or text links to `[[<name>]]`. Search the folder for `[[<name>]]` and `[[<name>|`.
4. **Group what you found by type**, newest first: journal entries (by date), notes, people, projects and goals.
5. **Answer** in the person's words: what it is, where it stands, the latest that happened, open questions. Link every note you mention as `[[Note]]` so they can open it.

Read only. Change nothing unless they ask.
