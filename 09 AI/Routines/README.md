The jobs your AI does again and again, one file each: what it is, when it is due, and the steps. A routine file only describes the job; nothing here runs on its own.

| Routine | When |
| --- | --- |
| [[Daily inbox sort]] | every morning |
| [[Weekly review]] | once a week, Friday afternoon or Sunday evening |

**How a routine runs.** Ask for it ("run my daily inbox sort") and any AI reads its file and does it. At the start of a session your AI looks here for a routine that is due and offers to run it; it never runs one without asking. To run one on a schedule, use a scheduler on your computer (Claude Code's scheduled tasks, or your system's own: launchd on a Mac, Task Scheduler on Windows) with a line like `claude -p "run the daily inbox sort"` in this folder. A schedule on your computer runs only while it is on and awake.

**A routine of your own.** Copy a file, rename it, and change the When and the steps. Keep the steps short: the skills in `09 AI/Skills/` hold the how.
