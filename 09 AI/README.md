# 09 AI

Your AI's own folder: how it works here, and its record. Whichever AI you point at this folder (Claude, ChatGPT, Codex, Gemini or the next one) works inside it and keeps its notes here, so the record stays with you when you change tools.

| Here | What it holds |
| --- | --- |
| `Skills/` | how your AI does the work here, one folder per skill (capture, weekly review and the rest). Copies sit in `.agents/skills` and `.claude/skills`, where AI tools look; the Objects plugin keeps them up to date. |
| `Routines/` | the jobs your AI does again and again, one file each: what, when, the steps. They only describe the job; your AI offers one when it is due, or you ask for it. |
| `Memory.md` | what your AI has learned about how you work: preferences and corrections. It reads this first and adds to it when you correct it. Edit it any time. |
| `Decisions.md` | the standing decisions, dated, with why: what holds until you change it. Your AI adds a line when you decide; it never goes against one without asking. |
| `Log/YYYY/MM/YYYY-MM-DD.md` | what was done in this folder, one file a day: when, which AI, where, what changed. Earlier entries are never edited. |
| `Reviews/YYYY/YYYY-Www.md` | the weekly reviews: what happened, what worked, what to refine, the next week's priorities. |

Your Daily Notes are what you wrote. The Log is what your AI did. Read both in the weekly review: that is the Refine in ICOR.

`AGENTS.md`, in the top folder, is where every AI starts reading. `AboutMe.md`, beside it, is who you are: your AI reads it next and takes it into account in everything it does, read-only. Only you write it. Then your AI comes here.

**AboutMe.md or Memory.md?** AboutMe is who you are, in your words, and changes rarely. Memory is how you like your AI to work, and your AI adds to it.
