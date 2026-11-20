---
name: check-quality
description: Check the ICOR for Life folder for notes that connect to nothing, missing or invented fields, values the schema does not allow, links to notes that do not exist, and captures still waiting, then propose repairs. Use when the person says "check my notes", "is my folder in order?", or after filing by hand.
---

# Check quality

1. `python3 _System/Tools/check-quality.py` (add `--json` for the data; `--write` saves the report the plugins show). It measures
   against `_System/schema.json`.
2. Group the findings: **broken** (fix now), **attention** (worth fixing), **info**.
3. Propose each repair in one line and **ask before you change** anything the person made. Typical repairs:
   - a note with no link: ask what it belongs to and add the link, or offer to remove it
   - an invented field: move its value into a real field, or ask
   - a value outside the allowed set: pick the right one with the person
   - a link to a missing note: create the note (skill **new-object**) or fix the spelling
4. Run the check again and report the new state in one line.
