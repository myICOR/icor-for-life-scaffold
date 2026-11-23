---
name: life-snapshot
description: Show where the person stands in their ICOR for Life folder - their goals, the projects in focus, this week's priorities, today's highlight, their Key Elements and the topics with recent attention. Use when they ask "where do I stand?", "what are my goals?", "what should I focus on?".
---

# Life snapshot

`python3 _System/Tools/life-snapshot.py --brief` answers the everyday questions from the folder itself:
goals, the projects in focus (`focus_rank` 1 to 3), this week's priorities, today's highlight, Key Elements, and the
topics with recent attention. `--json` for the data, `--write` to save the report for the plugins.

Read it, then tell the person in a few lines, with `[[links]]`. Do not invent priorities; if the week has none, ask
them for one and use skill **weekly-review**.

Set a project's focus: `python3 _System/Tools/set-property.py "02 Inner World/My Life/Projects/<Project>.md" focus_rank 1` (at most three projects carry one).
