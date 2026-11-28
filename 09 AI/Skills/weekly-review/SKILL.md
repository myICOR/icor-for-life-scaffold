---
name: weekly-review
description: Run the ICOR weekly review in the person's ICOR for Life folder - leftovers in the inbox and scratchpad, the reading queue, the week's journal recap, and the priorities for the coming week. Use when they say "weekly review" or "plan my week".
---
# Weekly review

Fifteen minutes. Six looks back, one forward, and one page to keep it. Ask, do not decide for them.

1. **Leftovers**: new sources in `06 Sources` that link to nothing yet (skill **process-outer-world**). Ask whether anything from the week's scratchpad days is worth carrying on (skill **process-scratchpad**); leaving it is fine.
2. **The Workbench**: each folder in `08 Workbench/` (not `Done/`). Read its `brief.md`: is it done, waiting, or still going? For finished work, file what lasts as objects (skill **new-object**: a note, a project update, a source) and move the folder to `08 Workbench/Done/`. Update the "Next" line of the rest.
3. **What your AI did**: the week's files in `09 AI/Log/`, as a few lines: what got done, what was left half way. Anything the person wants done differently goes into `09 AI/Memory.md`.
4. **Quality**: skill **check-quality** over the week's notes.
5. **Reading queue**: sources in `06 Sources` with `consumed: false`. One line each: read it this week, mark it consumed, or let it wait.
6. **The week in the journal**: the week's entries as a short recap, headlines only, with links.
7. **Forward**: the person names the week's priorities. Write each one: `python3 _System/Tools/planner-week.py ensure`, then `python3 _System/Tools/planner-week.py add-priority "<priority>"`. Today's highlight: `python3 _System/Tools/planner-week.py set-highlight "<highlight>"`.
8. **Keep it**: write the review to `09 AI/Reviews/YYYY/YYYY-Www.md` (this week's ISO week): frontmatter `type: review`, `week: YYYY-Www`, `created`; then what happened, what worked, what to refine, the priorities. Log it in today's AI log.
