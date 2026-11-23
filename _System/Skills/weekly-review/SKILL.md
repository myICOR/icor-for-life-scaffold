---
name: weekly-review
description: Run the ICOR weekly review in the person's ICOR for Life folder - leftovers in the inbox and scratchpad, the reading queue, the week's journal recap, and the priorities for the coming week. Use when they say "weekly review" or "plan my week".
---

# Weekly review

Fifteen minutes. Five looks back, one forward. Ask, do not decide for them.

1. **Leftovers**: new sources in `03 Outer World` that link to nothing yet (skill **process-outer-world**). Ask whether
   anything from the week's scratchpad days is worth carrying on (skill **process-scratchpad**); leaving it is fine.
2. **Finished work**: anything the person finished this week outside the folder (with you, in another tool) that
   belongs here. Offer to file each result as an object (skill **new-object**): a note, a project update, a source.
3. **Quality**: skill **check-quality** over the week's notes.
4. **Reading queue**: sources in `03 Outer World` with `consumed: false`. One line each: read it this week, mark it consumed, or
   let it wait.
5. **The week in the journal**: the week's entries as a short recap, headlines only, with links.
6. **Forward**: the person names the week's priorities. Write each one:
   `python3 _System/Tools/planner-week.py ensure`, then `python3 _System/Tools/planner-week.py add-priority "<priority>"`.
   Today's highlight: `python3 _System/Tools/planner-week.py set-highlight "<highlight>"`.
