---
name: process-outer-world
description: Connect what others made - books, articles, videos, podcasts, posts and papers in the ICOR for Life folder's 06 Sources (clipped with the Web Clipper or synced from Readwise) - to the projects, Key Elements and topics they serve, and keep the reading queue honest. Use when the person says "process my sources", "connect my clips", or asks what is in their reading queue.
---
# Process the Outer World

Every note in `06 Sources/` (and `06 Sources/Readwise/`) is a `source`: something someone else made. Sources stay where they are. Processing them means **connecting** them, not moving them. Fields: `_System/schema.json`, type `source`.

1. **Find what is waiting**: sources whose `projects`, `key_elements` and `topics` are all empty, newest first. Synced Readwise notes count too. A note there without `type: source` gets it: `python3 _System/Tools/set-property.py "06 Sources/<file>.md" type source`, then `source_type`.
2. **Connect each one** (skill **capture**, step 1): does it serve a project, touch a Key Element, belong to a topic? Add the link with `set-property.py` or by editing the list in its frontmatter (`topics: ["[[Deep Work]]"]`). It serves nothing: leave it unlinked and say so. That is allowed; most of what we read is not worth keeping.
3. **Their thought**: if `my_thought` holds one, or the person reacts to the source, that is theirs: a journal entry of type `thought` (skill **write-journal-entry**) or a note in `04 Notes/`, linking the source and the same topic. Their words verbatim.
4. **Reading queue**: sources with `consumed: false`. When the person has read or watched one, `set-property.py "06 Sources/<file>.md" consumed true`.

A **new source** by hand: `python3 _System/Tools/new-entity.py source "<Title>" --set source_type=<kind> --set source_url=<url> --link "[[<Topic>]]"`.

A **scan** in `01 Inbox/Scanner Inbox/` is not a source: it is a document you keep. Move the file to `10 Files/Documents/`, make a `document` note (skill **new-object**), then stamp the inbox file with `python3 _System/Tools/stamp-processed.py "<wrapper note>" --summary "<one line>" --capture "<path in 01 Inbox>"`.
