#!/usr/bin/env python3
"""test-life-snapshot.py: the fixture suite behind life-snapshot.py.

Builds a throwaway vault in a temp folder, one fixture per rule the script
claims, and asserts the script says what it claims. Every negative control
here is a signal the score must NOT count (a session log, an mtime, a
processed scratchpad counted twice), and the suite fails if the score moves.

Run it with --break-me to prove the suite itself can go red: it asserts the
opposite of one held rule and the run must end in FAIL.

Usage:  test-life-snapshot.py [--break-me]
Exit 0 = every case held. Exit 1 = a case did not.
"""
import datetime
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

# NO BYTECODE IN THE TREE WE ARE POINTED AT. This script importlib-loads a
# sibling out of Scripts/, and stock CPython then writes
# Scripts/__pycache__/<sibling>.cpython-3NN.pyc beside it, which is INSIDE the
# vault or the repo it was asked to read. A script that writes into the thing
# it measures is a script whose measurement nobody can trust, and the write is
# invisible under macOS's /usr/bin/python3, which redirects bytecode to its own
# cache (Conrad Froehling, 2026-09-16). PYTHONDONTWRITEBYTECODE is read at
# interpreter STARTUP, so only this assignment reaches a process already
# running.
sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "life-snapshot.py"
PY = sys.executable
BREAK = "--break-me" in sys.argv[1:]

_spec = importlib.util.spec_from_file_location("life_snapshot", SCRIPT)
LS = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(LS)

# The two writers this suite also covers: the week note and the frontmatter
# setter. Loaded by path for their constants; run as subprocesses for their
# behaviour, the same way life-snapshot.py is.
PW_SCRIPT = HERE / "planner-week.py"
SP_SCRIPT = HERE / "set-property.py"
_pwspec = importlib.util.spec_from_file_location("planner_week", PW_SCRIPT)
PW = importlib.util.module_from_spec(_pwspec)
_pwspec.loader.exec_module(PW)
_spspec = importlib.util.spec_from_file_location("set_property", SP_SCRIPT)
SP = importlib.util.module_from_spec(_spspec)
_spspec.loader.exec_module(SP)

TODAY = datetime.date.today()
fails = []
checks = 0


def check(name, ok, detail=""):
    global checks
    checks += 1
    if ok:
        print("  ok   %s" % name)
    else:
        fails.append("%s: %s" % (name, detail))
        print("  FAIL %s: %s" % (name, detail))


# ---------------------------------------------------------------------------
# PLANTING A SYMLINK IS NOT SOMETHING EVERY PLATFORM LETS US DO
# ---------------------------------------------------------------------------
#
# Six cases below plant a symlink in order to prove that life-snapshot.py
# refuses to follow one. Windows refuses to create one at all for an
# unprivileged shell with Developer Mode off, which is the default, and the
# first of those calls raised OSError 1314 and took the whole fixture suite
# down with it. run-red-tests.py then reported that as a life-snapshot guard
# failure, which is a red pointing at the wrong thing (Conrad Froehling,
# 2026-09-16).
#
# Where nothing can plant a symlink these cases have nothing to measure, so
# they skip BY NAME and the run says how many skipped. A skip is never a green:
# the summary line carries the count either way.
skipped = []
_symlink_why = None


def can_symlink():
    """True when this process may create a symlink here. Probed once, for real."""
    global _symlink_why
    if _symlink_why is None:
        with tempfile.TemporaryDirectory() as _d:
            _t = Path(_d) / "target"
            _t.write_text("x\n", encoding="utf-8")
            try:
                os.symlink(_t, Path(_d) / "link")
                _symlink_why = ""
            except (OSError, NotImplementedError, AttributeError) as exc:
                _symlink_why = ("this platform will not let this process create "
                                "a symlink (%s), so there is nothing to plant "
                                "and the case is skipped on this platform" % exc)
    return not _symlink_why


def skip_symlink_case(name):
    skipped.append(name)
    print("  SKIP %s: %s" % (name, _symlink_why))


def day(offset):
    return (TODAY - datetime.timedelta(days=offset)).isoformat()


def write(root, rel, text):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


def rooms(root, planner=True, scratchpad=True, goals=True, notes=True):
    made = ["04 Inner World/My Life/Projects",
            "04 Inner World/My Life/Key Elements",
            "04 Inner World/My Life/Topics",
            "04 Inner World/Journal"]
    if goals:
        made.append("04 Inner World/My Life/Goals")
    if notes:
        made.append("04 Inner World/Notes")
    if planner:
        made.append("02 Planner/Todoist")
    if scratchpad:
        made.append("00 Daily Scratchpad")
    for d in made:
        (root / d).mkdir(parents=True, exist_ok=True)


def journal(root, offset, slug, front_extra="", body=""):
    d = day(offset)
    y, m = d[:4], d[5:7]
    write(root, "04 Inner World/Journal/%s/%s/%s-%s.md" % (y, m, d, slug),
          "---\ntype: journal\ndate: %s\n%s---\n%s\n" % (d, front_extra, body))


def run(root, *args):
    return subprocess.run([PY, str(SCRIPT), str(root)] + list(args),
                          capture_output=True, text=True)


def pw(root, *args):
    return subprocess.run([PY, str(PW_SCRIPT)] + list(args)
                          + ["--root", str(root)], capture_output=True, text=True)


def sp(root, *args):
    return subprocess.run([PY, str(SP_SCRIPT)] + list(args)
                          + ["--root", str(root)], capture_output=True, text=True)


def snap(root, *args):
    r = run(root, "--json", *args)
    if r.returncode != 0:
        return None, r
    return json.loads(r.stdout), r


def by_name(items, name):
    for i in items:
        if i["name"] == name:
            return i
    return None


with tempfile.TemporaryDirectory() as td:
    TD = Path(td)

    # === case group 1: the attention score ================================
    print("attention")
    V = TD / "attention"
    rooms(V)
    for t in ("Topic A", "Topic B", "Topic C", "Topic D"):
        write(V, "04 Inner World/My Life/Topics/%s.md" % t,
              "---\ntype: topic\n---\n")
    journal(V, 3, "a-one", "linked_topics: [\"[[Topic A]]\"]\n")
    journal(V, 10, "a-two", "linked_topics: [\"[[Topic A]]\"]\n")
    journal(V, 40, "a-old", "linked_topics: [\"[[Topic A]]\"]\n")
    # one entry naming the same topic five times is ONE event
    journal(V, 3, "a-many", "linked_topics: [\"[[Topic B]]\"]\n",
            "[[Topic B]] [[Topic B]] [[Topic B]] [[Topic B]]\n")
    # negative control: the team's own record is not the user's attention
    write(V, "06 AI Team/AI Team Knowledge/Session Logs/2026/09/log.md",
          "---\ndate: %s\n---\nWorked on [[Topic C]] all day.\n" % day(1))
    # negative control: a touched file is not an attended file
    p = write(V, "04 Inner World/My Life/Topics/Topic D.md",
              "---\ntype: topic\n---\n")
    os.utime(p, (time.time(), time.time()))

    rep, r = snap(V)
    check("exit 0 on a populated vault", rep is not None, r.stderr)
    tops = {t["name"]: t["attention"] for t in
            [x for x in rep["topics"]["hot"]]} if rep else {}
    a = tops.get("Topic A")
    check("Topic A: 3d and 10d counted, 40d not (n7 1, n14 2, n30 2, score 5)",
          a == {"n7": 1, "n14": 2, "n30": 2, "score": 5,
                "last_seen": day(3)}, str(a))
    b = tops.get("Topic B")
    check("five mentions in one entry are ONE event (n30 1, score 3)",
          b and b["n30"] == 1 and b["score"] == 3, str(b))
    allranked = {t["name"] for t in rep["topics"]["hot"]} if rep else set()
    check("session-log mention scores 0 (Topic C is not ranked hot)",
          "Topic C" not in allranked, str(allranked))
    check("mtime alone scores 0 (Topic D is not ranked hot)",
          "Topic D" not in allranked, str(allranked))
    # three of the four entries are inside the window; the 40-day one is not
    # counted and does not appear in the source count either
    check("sources_counted names the journal only, window respected",
          rep["topics"]["sources_counted"]["journal"] == 3
          and rep["topics"]["sources_counted"]["notes"] == 0,
          str(rep["topics"]["sources_counted"]))

    # === case group 2: the scratchpad is never counted twice ==============
    print("double counting")
    V = TD / "scratchpad"
    rooms(V)
    write(V, "04 Inner World/My Life/Topics/Topic B.md", "---\ntype: topic\n---\n")
    write(V, "00 Daily Scratchpad/%s.md" % day(2),
          "---\nprocessed: true\n---\nthinking about [[Topic B]]\n")
    journal(V, 2, "from-the-pad", "linked_topics: [\"[[Topic B]]\"]\n")
    rep, r = snap(V)
    b = by_name(rep["topics"]["hot"], "Topic B") if rep else None
    check("a processed scratchpad plus its journal entry is ONE event",
          b and b["attention"]["n30"] == 1 and b["attention"]["score"] == 3,
          str(b))

    V = TD / "scratchpad-raw"
    rooms(V)
    write(V, "04 Inner World/My Life/Topics/Topic B.md", "---\ntype: topic\n---\n")
    write(V, "00 Daily Scratchpad/%s.md" % day(2), "thinking about [[Topic B]]\n")
    rep, r = snap(V)
    b = by_name(rep["topics"]["hot"], "Topic B") if rep else None
    check("an UNPROCESSED scratchpad is counted while it is raw",
          b and b["attention"]["n30"] == 1, str(b))
    check("sources_counted names the scratchpad",
          rep["topics"]["sources_counted"]["scratchpad"] == 1,
          str(rep["topics"]["sources_counted"]))

    # === case group 3: both value shapes ==================================
    print("link shapes")
    V = TD / "shapes"
    rooms(V)
    write(V, "04 Inner World/My Life/Topics/scaffold-over-model.md",
          "---\nname: Scaffold over model\n---\n")
    journal(V, 1, "slug-shape", "linked_topics:\n  - scaffold-over-model\n")
    journal(V, 2, "wikilink-shape",
            "linked_topics: [\"[[scaffold-over-model]]\"]\n")
    rep, r = snap(V)
    t = by_name(rep["topics"]["hot"], "Scaffold over model") if rep else None
    check("a slug and a quoted wikilink resolve to the same topic",
          t and t["attention"]["n30"] == 2 and t["attention"]["score"] == 6,
          str(t))

    # === case group 4: focus_rank =========================================
    print("focus")
    V = TD / "focus"
    rooms(V)
    for i, rank in enumerate((1, 2, 3, 3), start=1):
        write(V, "04 Inner World/My Life/Projects/P%d.md" % i,
              "---\ntype: project\nstatus: active\nfocus_rank: %d\n---\n" % rank)
    rep, r = snap(V)
    ids = [f["id"] for f in rep["findings"]] if rep else []
    check("four ranked projects raise focus_over_max",
          "focus_over_max" in ids, str(ids))
    check("the script reports all four, it does not censor",
          len(rep["projects"]["focus"]) == 4, str(len(rep["projects"]["focus"])))
    check("focus[] is in rank order",
          [p["focus_rank"] for p in rep["projects"]["focus"]] == [1, 2, 3, 3],
          str([p["focus_rank"] for p in rep["projects"]["focus"]]))
    check("a repeated rank raises focus_duplicate_rank",
          "focus_duplicate_rank" in ids, str(ids))
    check("a vault WITH ranks has no focus_rank degraded entry",
          "focus_rank" not in [d["source"] for d in rep["degraded"]],
          str(rep["degraded"]))

    V = TD / "focus-none"
    rooms(V)
    write(V, "04 Inner World/My Life/Projects/P1.md",
          "---\ntype: project\nstatus: active\n---\n")
    rep, r = snap(V)
    check("no rank anywhere: focus[] empty and degraded names focus_rank",
          rep["projects"]["focus"] == []
          and "focus_rank" in [d["source"] for d in rep["degraded"]],
          str(rep["degraded"]))

    V = TD / "focus-paused"
    rooms(V)
    write(V, "04 Inner World/My Life/Projects/P1.md",
          "---\ntype: project\nstatus: paused\nfocus_rank: 1\n---\n")
    rep, r = snap(V)
    check("focus_rank_not_active fires on a paused project",
          "focus_rank_not_active" in [f["id"] for f in rep["findings"]],
          str(rep["findings"]))

    # === case group 5: goals ==============================================
    print("goals")
    V = TD / "goals"
    rooms(V)
    write(V, "04 Inner World/My Life/Goals/Late.md",
          "---\ntype: goal\nstatus: active\ntarget_date: %s\n---\n" % day(30))
    write(V, "04 Inner World/My Life/Goals/Later.md",
          "---\ntype: goal\nstatus: active\ntarget_date: %s\n---\n" % day(-10))
    write(V, "04 Inner World/My Life/Goals/Someday.md",
          "---\ntype: goal\nstatus: active\ntarget_date:\n---\n")
    write(V, "04 Inner World/My Life/Goals/Done.md",
          "---\ntype: goal\nstatus: achieved\n---\n")
    rep, r = snap(V)
    check("a closed goal is not open", len(rep["goals"]["open"]) == 3,
          str([g["name"] for g in rep["goals"]["open"]]))
    check("order is target_date ascending, nulls last",
          [g["name"] for g in rep["goals"]["open"]] == ["Late", "Later", "Someday"],
          str([g["name"] for g in rep["goals"]["open"]]))
    check("an active goal past its target date is a finding",
          "goal_overdue_active" in [f["id"] for f in rep["findings"]],
          str(rep["findings"]))
    check("achieved_90d is empty, never guessed",
          rep["goals"]["achieved_90d"] == [], str(rep["goals"]["achieved_90d"]))

    # === case group 5b: the three carrier shapes (GL-002 v1.52) ===========
    print("goal carriers")
    V = TD / "carriers"
    rooms(V)
    write(V, "04 Inner World/My Life/Goals/Floor.md",
          "---\ntype: goal\nstatus: active\n"
          "linked_projects:\n  - podcast-relaunch\n"
          "linked_habits:\n  - weekly-cadence\n"
          "linked_workstreams:\n  - WS-013-video-publishing-lifecycle\n"
          "linked_topics:\n  - revenue-growth\n---\n")
    write(V, "04 Inner World/My Life/Goals/Public.md",
          "---\ntype: goal\nstatus: not-achieved\n"
          "workstreams: [\"[[WS-1002-weekly-review|WS-1002]]\"]\n---\n")
    write(V, "04 Inner World/My Life/Goals/Plain.md",
          "---\ntype: goal\nstatus: active\n---\n")
    rep, r = snap(V)
    floor = by_name(rep["goals"]["open"], "Floor")
    check("carriers carries the three shapes: projects, habits, workstreams",
          floor is not None
          and sorted(floor["carriers"]) == ["habits", "projects", "workstreams"],
          str(floor and floor["carriers"]))
    check("the private `linked_workstreams` stem is read verbatim",
          floor is not None
          and floor["carriers"]["workstreams"] == ["WS-013-video-publishing-lifecycle"],
          str(floor and floor["carriers"]))
    check("a Topic is never a carrier (negative control)",
          floor is not None
          and "revenue-growth" not in json.dumps(floor["carriers"]),
          str(floor and floor["carriers"]))
    pub = by_name(rep["goals"]["open"], "Public")
    check("the public `workstreams` wikilink shape resolves to the WS stem",
          pub is not None
          and pub["carriers"]["workstreams"] == ["WS-1002-weekly-review"],
          str(pub and pub["carriers"]))
    plain = by_name(rep["goals"]["open"], "Plain")
    check("a goal with no carrier field carries three empty lists, never a missing key",
          plain is not None
          and plain["carriers"] == {"projects": [], "habits": [], "workstreams": []},
          str(plain and plain["carriers"]))

    print("no goals room")
    V = TD / "no-goals"
    rooms(V, goals=False)
    rep, r = snap(V)
    check("a missing Goals room is degraded, not a crash",
          rep is not None and rep["goals"]["open"] == []
          and "goals" in [d["source"] for d in rep["degraded"]],
          (r.stderr or str(rep["degraded"] if rep else None)))
    check("exit 0 with a missing room", r.returncode == 0, str(r.returncode))

    # === case group 6: the weekly note ====================================
    print("weekly note")
    V = TD / "no-week"
    rooms(V)
    rep, r = snap(V)
    check("no weekly note: weekly_goals.reason is filled",
          rep["weekly_goals"]["reason"], str(rep["weekly_goals"]))
    check("no weekly note: highlight.reason is filled",
          rep["highlight"]["reason"], str(rep["highlight"]))
    check("no weekly note: degraded names planner_week",
          "planner_week" in [d["source"] for d in rep["degraded"]],
          str(rep["degraded"]))
    check("no weekly note: exit is still 0", r.returncode == 0, str(r.returncode))

    V = TD / "week"
    rooms(V)
    y, w, _ = TODAY.isocalendar()
    week_id = "%04d-W%02d" % (y, w)
    write(V, "02 Planner/Weeks/%s.md" % week_id,
          "---\ntype: planner-week\nweek: %s\n---\n\n"
          "## Weekly priorities\n%s\n"
          "- [ ] Ship the explainer video\n"
          "- [x] Book the sleep lab follow-up\n"
          "a plain line that is not a priority\n\n"
          "## Daily highlights\n%s\n"
          "| Date | Highlight | Done |\n|---|---|---|\n"
          "| %s | Record episode 3 | _ |\n"
          "| %s | Paco review call | Y |\n"
          % (week_id, LS.PRIORITIES_SENTINEL, LS.HIGHLIGHTS_SENTINEL,
             TODAY.isoformat(), day(1)))
    rep, r = snap(V)
    wg = rep["weekly_goals"]
    check("the checklist reads 2 priorities, 1 done, the plain line ignored",
          len(wg["items"]) == 2 and wg["done_count"] == 1, str(wg))
    check("no planner_week degraded entry when the note is there",
          "planner_week" not in [d["source"] for d in rep["degraded"]],
          str(rep["degraded"]))
    h = rep["highlight"]
    check("highlight.text is today's row", h["text"] == "Record episode 3", str(h))
    check("highlight.done is null for the `_` marker", h["done"] is None, str(h))
    check("recent holds yesterday, marked done",
          len(h["recent"]) == 1 and h["recent"][0]["done"] is True, str(h["recent"]))

    V = TD / "week-over-max"
    rooms(V)
    write(V, "02 Planner/Weeks/%s.md" % week_id,
          "---\ntype: planner-week\nweek: %s\n---\n\n## Weekly priorities\n%s\n%s\n"
          % (week_id, LS.PRIORITIES_SENTINEL,
             "\n".join("- [ ] priority %d" % i for i in range(1, 8))))
    rep, r = snap(V)
    check("more than the weekly cap is a finding",
          "weekly_goals_over_max" in [f["id"] for f in rep["findings"]],
          str(rep["findings"]))

    # === case group 7: the planner ========================================
    print("planner")
    V = TD / "no-planner"
    rooms(V, planner=False)
    rep, r = snap(V)
    srcs = [d["source"] for d in rep["degraded"]]
    check("a missing 02 Planner is degraded, exit 0",
          r.returncode == 0 and "planner" in srcs, str(srcs))

    V = TD / "planner-unlinked"
    rooms(V)
    write(V, "02 Planner/Todoist/Task.md",
          "---\ntype: planner-item\nstatus: open\nplanned_day: %s\n"
          "weekly_goal: false\n---\n" % TODAY.isoformat())
    rep, r = snap(V)
    check("planner items with no link field raise the planner_link gap",
          "planner_link" in [d["source"] for d in rep["degraded"]],
          str(rep["degraded"]))

    # === case group 8: the empty vault ====================================
    print("empty vault")
    V = TD / "empty"
    rooms(V)
    rep, r = snap(V)
    check("empty vault: exit 0", r.returncode == 0, r.stderr)
    check("empty vault: schema 1", rep and rep["schema"] == 1, str(rep and rep["schema"]))
    check("empty vault: every list is empty",
          rep["goals"]["open"] == [] and rep["projects"]["active"] == []
          and rep["key_elements"] == [] and rep["topics"]["hot"] == [],
          json.dumps({"g": rep["goals"]["open"], "p": rep["projects"]["active"]}))
    check("empty vault: the only degraded source is the missing week note",
          [d["source"] for d in rep["degraded"]] == ["planner_week"],
          str(rep["degraded"]))
    check("empty vault: no findings", rep["findings"] == [], str(rep["findings"]))

    # === case group 9: refusals ===========================================
    print("refusals")
    V = TD / "not-a-vault"
    V.mkdir()
    r = run(V, "--json", "--write")
    check("a root without '04 Inner World' exits 1", r.returncode == 1,
          str(r.returncode))
    check("and writes no file",
          not (V / ".icor-for-life/scripts/snapshot.json").exists())

    V = TD / "secret"
    rooms(V)
    write(V, "04 Inner World/My Life/Goals/Ship it.md",
          "---\ntype: goal\nstatus: active\n"
          "name: \"ship with sk-abcdefghijklmnopqrstuvwxyz012345\"\n---\n")
    r = run(V, "--write")
    check("a secret-shaped value refuses the whole write", r.returncode == 1,
          str(r.returncode) + r.stdout)
    check("and says so", "secret-shaped" in (r.stderr + r.stdout), r.stderr)
    check("and no file is left behind",
          not (V / ".icor-for-life/scripts/snapshot.json").exists())
    check("and no temp file is left behind",
          not list((V / ".icor-for-life/scripts").glob("*.tmp"))
          if (V / ".icor-for-life/scripts").is_dir() else True)

    # === case group 10: the write, the brief and staleness ================
    print("write, brief, staleness")
    V = TD / "write"
    rooms(V)
    write(V, "04 Inner World/My Life/Goals/Run a marathon.md",
          "---\ntype: goal\nstatus: not-achieved\nkey_elements: [\"[[Health]]\"]\n---\n")
    write(V, "04 Inner World/My Life/Key Elements/Health.md",
          "---\ntype: key-element\n---\n")
    r = run(V, "--write")
    dest = V / ".icor-for-life/scripts/snapshot.json"
    check("--write writes the file", dest.is_file(), r.stderr)
    written = json.loads(dest.read_text(encoding="utf-8"))
    check("the written file carries schema, generated_at, degraded, findings",
          all(k in written for k in ("schema", "generated_at", "degraded",
                                     "findings")), str(sorted(written)))
    check("the public `not-achieved` status counts as an open goal",
          len(written["goals"]["open"]) == 1, str(written["goals"]["open"]))
    check("the public `key_elements` wikilink shape resolves to the key element",
          written["key_elements"][0]["open_goals"] == 1,
          str(written["key_elements"]))
    r = run(V, "--brief")
    lines = [l for l in r.stdout.splitlines() if l.strip()]
    check("--brief is short enough to read (<= 25 lines)",
          0 < len(lines) <= 25, str(len(lines)))
    check("--brief names the six answers",
          all(k in r.stdout for k in ("Goals (", "Focus (", "Weekly priorities",
                                      "Daily highlight", "Key elements (",
                                      "Hot topics")), r.stdout)
    check("--brief says whether it is fresh or stale",
          "(fresh)" in r.stdout or "(stale)" in r.stdout, r.stdout)

    fresh = dict(written)
    fresh["generated_at"] = datetime.datetime.now(datetime.timezone.utc) \
        .strftime("%Y-%m-%dT%H:%M:%SZ")
    fresh["generated_local_date"] = TODAY.isoformat()
    check("a snapshot written just now is not stale", not LS.is_stale(fresh))
    old = dict(fresh)
    old["generated_at"] = (datetime.datetime.now(datetime.timezone.utc)
                           - datetime.timedelta(days=1)) \
        .strftime("%Y-%m-%dT%H:%M:%SZ")
    old["generated_local_date"] = day(1)
    check("a snapshot backdated by a day is stale", LS.is_stale(old))
    broken = dict(fresh)
    broken["generated_at"] = "not a date"
    check("a snapshot whose stamp cannot be read is stale, never fresh",
          LS.is_stale(broken))

    # === case group 11: one reader, not two ===============================
    print("reader parity")
    if (HERE / "check-quality.py").is_file():
        check("the shared readers are imported from check-quality.py",
              LS.READER_SOURCE == "check-quality.py", LS.READER_SOURCE)
        sample = "---\nname: x\ntopics: [\"[[A]]\", b]\n---\nbody [[C|alias]]\n"
        f1, b1 = LS.split_front(sample)
        f2, b2 = LS._fb_split_front(sample)
        check("imported and fallback split_front agree", (f1, b1) == (f2, b2))
        check("imported and fallback parse_front agree",
              LS.parse_front(f1) == LS._fb_parse_front(f2))
        check("imported and fallback link_name agree",
              LS.link_name("[[C|alias]]") == LS._fb_link_name("[[C|alias]]")
              == "C")
    else:
        check("no check-quality.py here, so the fallback readers run",
              LS.READER_SOURCE == "built-in fallback", LS.READER_SOURCE)


    # === case group 12: the secret scan, one red case per family =========
    # Vex F1, 2026-09-15. Every sample is ASSEMBLED AT RUNTIME from pieces,
    # so this file never carries a secret-shaped string of its own and the
    # outbound guard has nothing to fire on. Each case is a RED control:
    # the writer must refuse, exit 1, and write no file.
    print("secret scan")
    A = "A" * 40
    D = "7" * 9
    samples = {
        "jwt":                       "ey" + "J" + A[:12] + "." + A[:12] + "." + A[:12],
        "supabase_secret":           "sb" + "_secret_" + A[:24],
        "resend_key":                "re" + "_" + A[:8] + "_" + A[:24],
        "openai_key":                "sk" + "-" + A[:30],
        "anthropic_key":             "sk" + "-ant-" + A[:30],
        "github_token":              "gh" + "p_" + A[:36],
        "slack_token":               "xo" + "xb-" + A[:20],
        "stripe_key":                "sk" + "_live_" + A[:26],
        "telegram_token":            D + ":" + A[:36],
        "google_refresh":            "1" + "//" + A[:30],
        "pg_dsn_password":           "postgres" + "://user:" + A[:12] + "@host/db",
        "private_key_block":         "-----BEGIN " + "PRIVATE KEY-----",
        "aws_access_key_id":         "AK" + "IA" + "B" * 16,
        "bearer_header":             "Bear" + "er " + A[:30],
        "generic_secret_assignment": "SOME" + "_API_KEY" + "=" + A[:24],
    }
    families = [n for n, _rx in LS.SECRET_SHAPES]
    check("the scan carries every write-guard family",
          all(f in families for f in
              ("jwt", "supabase_secret", "resend_key", "resend_key_ctx",
               "openai_key", "anthropic_key", "github_token", "slack_token",
               "stripe_key", "telegram_token", "google_refresh",
               "pg_dsn_password", "private_key_block",
               "generic_secret_assignment")), str(families))
    for family, sample in samples.items():
        check("unit: %s is recognised" % family,
              family in LS.secret_findings(sample),
              str(LS.secret_findings(sample)))

    y, w, _ = TODAY.isocalendar()
    week_id = "%04d-W%02d" % (y, w)
    for family, sample in sorted(samples.items()):
        V = TD / ("secret-" + family)
        rooms(V)
        # the likeliest real paste: a checklist line in the week note
        write(V, "02 Planner/Weeks/%s.md" % week_id,
              "---\ntype: planner-week\nweek: %s\n---\n\n"
              "## Weekly priorities\n%s\n- [ ] rotate %s\n"
              % (week_id, LS.PRIORITIES_SENTINEL, sample))
        r = run(V, "--write")
        wrote = (V / ".icor-for-life/scripts/snapshot.json").exists()
        check("end to end: %s in a priority line refuses and writes nothing"
              % family, r.returncode == 1 and not wrote,
              "exit %s, wrote %s" % (r.returncode, wrote))
        check("end to end: %s refusal names the family, never the value"
              % family, family in r.stderr and sample not in r.stderr,
              r.stderr)

    check("the three writers carry the SAME pattern list",
          [n for n, _ in LS.SECRET_SHAPES] == [n for n, _ in PW.SECRET_SHAPES]
          == [n for n, _ in SP.SECRET_SHAPES],
          "life-snapshot %d, planner-week %d, set-property %d"
          % (len(LS.SECRET_SHAPES), len(PW.SECRET_SHAPES),
             len(SP.SECRET_SHAPES)))

    # === case group 13: the write path stays inside the vault ============
    # Vex F2 and F6.
    print("write path")
    outside = TD / "outside"
    outside.mkdir(exist_ok=True)

    if not can_symlink():
        skip_symlink_case("G: a planted snapshot.json.tmp symlink does not "
                          "overwrite its target")
    else:
        V = TD / "symlink-tmp"
        rooms(V)
        victim = outside / "victim-tmp.txt"
        victim.write_text("untouched\n", encoding="utf-8")
        (V / ".icor-for-life/scripts").mkdir(parents=True, exist_ok=True)
        os.symlink(victim, V / ".icor-for-life/scripts/snapshot.json.tmp")
        r = run(V, "--write")
        check("G: a planted snapshot.json.tmp symlink does not overwrite its target",
              victim.read_text(encoding="utf-8") == "untouched\n",
              victim.read_text(encoding="utf-8")[:40])

    if not can_symlink():
        skip_symlink_case("H: a symlinked scripts/ folder refuses, exit 1")
    else:
        V = TD / "symlink-dir"
        rooms(V)
        elsewhere = outside / "elsewhere"
        elsewhere.mkdir(exist_ok=True)
        (V / ".icor-for-life").mkdir(parents=True, exist_ok=True)
        os.symlink(elsewhere, V / ".icor-for-life/scripts")
        r = run(V, "--write")
        check("H: a symlinked scripts/ folder refuses, exit 1",
              r.returncode == 1, "exit %s: %s" % (r.returncode, r.stderr))
        check("H: nothing was written outside the vault",
              not (elsewhere / "snapshot.json").exists(),
              str(list(elsewhere.iterdir())))

    V = TD / "replace-fails"
    rooms(V)
    (V / ".icor-for-life/scripts/snapshot.json").mkdir(parents=True,
                                                       exist_ok=True)
    r = run(V, "--write")
    leftovers = [f.name for f in (V / ".icor-for-life/scripts").iterdir()
                 if f.name.endswith(".tmp")]
    check("I: a failed swap exits 1", r.returncode == 1, r.stderr)
    check("I: a failed swap leaves no .tmp behind", leftovers == [],
          str(leftovers))

    V = TD / "write-ok"
    rooms(V)
    r = run(V, "--write")
    check("the ordinary write still lands", r.returncode == 0 and
          (V / ".icor-for-life/scripts/snapshot.json").is_file(), r.stderr)

    # === case group 14: VERSION is validated, not copied =================
    # Vex F3.
    print("scaffold_version")
    V = TD / "version-good"
    rooms(V)
    write(V, ".icor-for-life/VERSION", "1.24.1\n")
    rep, _r = snap(V)
    check("a semver VERSION is carried through",
          rep["scaffold_version"] == "1.24.1", str(rep["scaffold_version"]))

    V = TD / "version-junk"
    rooms(V)
    write(V, ".icor-for-life/VERSION",
          "SOME" + "_API_TOKEN" + "=" + "B" * 30 + "\nsecond line\n")
    rep, r = snap(V)
    check("E: a VERSION that is not a version becomes `unknown`",
          rep is not None and rep["scaffold_version"] == "unknown",
          str(rep["scaffold_version"]) if rep else r.stderr)
    check("E: and the reason is in degraded",
          "scaffold_version" in [d["source"] for d in rep["degraded"]],
          str(rep["degraded"]))

    if not can_symlink():
        skip_symlink_case("F: a symlinked VERSION is never read")
    else:
        V = TD / "version-symlink"
        rooms(V)
        target = outside / "some-file.txt"
        target.write_text("9.9.9\n", encoding="utf-8")
        (V / ".icor-for-life").mkdir(parents=True, exist_ok=True)
        os.symlink(target, V / ".icor-for-life/VERSION")
        rep, _r = snap(V)
        check("F: a symlinked VERSION is never read",
              rep["scaffold_version"] == "unknown", str(rep["scaffold_version"]))

    # === case group 15: planner-week.py, the writer ======================
    print("planner-week.py")
    V = TD / "pw"
    rooms(V)
    note = V / "02 Planner/Weeks" / ("%s.md" % week_id)

    r = pw(V, "ensure")
    check("ensure creates the note", r.returncode == 0 and note.is_file(),
          r.stderr)
    body = note.read_text(encoding="utf-8")
    check("ensure writes both sentinels, under Iris's headings",
          PW.PRIORITIES_SENTINEL in body and PW.HIGHLIGHTS_SENTINEL in body
          and "## Weekly priorities" in body and "## Daily highlights" in body,
          body)
    check("ensure writes type and the ISO week",
          "type: planner-week" in body and ("week: %s" % week_id) in body, body)
    before = note.read_bytes()
    r = pw(V, "ensure")
    check("ensure is idempotent and never overwrites",
          r.returncode == 0 and note.read_bytes() == before, r.stdout)

    pw(V, "add-priority", "Ship the explainer video")
    pw(V, "add-priority", "Book the sleep lab follow-up")
    r = pw(V, "add-priority", "ship the EXPLAINER video")
    check("a duplicate priority is not added twice",
          note.read_text(encoding="utf-8").count("Ship the explainer video") == 1,
          note.read_text(encoding="utf-8"))
    r = pw(V, "done-priority", "sleep lab")
    check("done-priority ticks exactly the matching line",
          "- [x] Book the sleep lab follow-up" in note.read_text(encoding="utf-8")
          and "- [ ] Ship the explainer video" in note.read_text(encoding="utf-8"),
          note.read_text(encoding="utf-8"))
    r = pw(V, "done-priority", "no such thing")
    check("done-priority on a line that is not there refuses",
          r.returncode == 1 and "FAIL" in r.stderr, r.stderr + r.stdout)

    # The second row must stay inside the current ISO week: `day(1)` on a
    # Monday is the previous week's Sunday, and the row would land in that
    # week's note instead. Anchor it to this week's Monday; on a Monday
    # itself take Tuesday, which also exercises a row added for a later day.
    monday = TODAY - datetime.timedelta(days=TODAY.weekday())
    other = monday if monday != TODAY else monday + datetime.timedelta(days=1)
    other_day = other.isoformat()
    pw(V, "set-highlight", "Record episode 3")
    pw(V, "set-highlight", "Paco review call", "--date", other_day)
    txt = note.read_text(encoding="utf-8")
    newer, older = (("Paco review call", "Record episode 3") if other > TODAY
                    else ("Record episode 3", "Paco review call"))
    check("set-highlight writes one row per date, newest on top",
          txt.count("| %s |" % TODAY.isoformat()) == 1
          and txt.count("| %s |" % other_day) == 1
          and txt.index(newer) < txt.index(older), txt)
    pw(V, "mark-highlight", "Y", "--date", other_day)
    pw(V, "set-highlight", "Record episode 4")
    txt = note.read_text(encoding="utf-8")
    check("set-highlight replaces a day's row in place, keeping the marker",
          txt.count("| %s |" % TODAY.isoformat()) == 1
          and "Record episode 3" not in txt and "Record episode 4" in txt, txt)
    check("mark-highlight writes the habit-log marker set",
          ("| %s | Paco review call | Y |" % other_day) in txt, txt)
    r = pw(V, "mark-highlight", "Q")
    check("an unknown marker is refused", r.returncode == 1, r.stderr)
    r = pw(V, "set-highlight", "out of range", "--date", day(40),
           "--week", week_id)
    check("a date outside the named week is refused", r.returncode == 1,
          r.stderr)

    # the reader and the writer agree on the same file
    rep, _r = snap(V)
    check("life-snapshot reads what planner-week wrote",
          len(rep["weekly_goals"]["items"]) == 2
          and rep["weekly_goals"]["done_count"] == 1
          and rep["highlight"]["text"] == "Record episode 4", str(rep["highlight"]))

    # Axon 10.1: a plain line under the sentinel is not a priority and is
    # untouched by the next write.
    V = TD / "pw-plain"
    rooms(V)
    note = V / "02 Planner/Weeks" / ("%s.md" % week_id)
    note.parent.mkdir(parents=True, exist_ok=True)
    note.write_text("---\ntype: planner-week\nweek: %s\n---\n\n"
                    "## Weekly priorities\n%s\n- [ ] one\n"
                    "a plain line that is not a priority\n"
                    % (week_id, PW.PRIORITIES_SENTINEL), encoding="utf-8")
    pw(V, "add-priority", "two")
    txt = note.read_text(encoding="utf-8")
    check("the plain line survives a write, byte for byte",
          "a plain line that is not a priority" in txt, txt)
    rep, _r = snap(V)
    check("and the reader counts 2, not 3",
          len(rep["weekly_goals"]["items"]) == 2, str(rep["weekly_goals"]))

    # Axon 10.1: the CRLF case.
    V = TD / "pw-crlf"
    rooms(V)
    note = V / "02 Planner/Weeks" / ("%s.md" % week_id)
    note.parent.mkdir(parents=True, exist_ok=True)
    crlf = ("---\r\ntype: planner-week\r\nweek: %s\r\n---\r\n\r\n"
            "## Weekly priorities\r\n%s\r\n- [ ] one\r\n\r\n"
            "## Daily highlights\r\n%s\r\n"
            "| Date | Highlight | Done |\r\n|---|---|---|\r\n"
            % (week_id, PW.PRIORITIES_SENTINEL, PW.HIGHLIGHTS_SENTINEL))
    note.write_bytes(crlf.encode("utf-8"))
    pw(V, "set-highlight", "a CRLF highlight")
    pw(V, "add-priority", "two")
    raw = note.read_bytes()
    check("CRLF: not one lone LF was introduced",
          raw.count(b"\n") == raw.count(b"\r\n"),
          "%d LF, %d CRLF" % (raw.count(b"\n"), raw.count(b"\r\n")))
    check("CRLF: the added lines are there",
          b"- [ ] two" in raw and b"a CRLF highlight" in raw, str(raw[:80]))
    rep, _r = snap(V)
    check("CRLF: the reader still reads it",
          rep["highlight"]["text"] == "a CRLF highlight", str(rep["highlight"]))

    r = pw(V, "add-priority", "rotate " + "sk" + "_live_" + "C" * 26)
    check("planner-week refuses a secret-shaped priority",
          r.returncode == 1 and "secret-shaped" in r.stderr, r.stderr)

    # === case group 16: set-property.py, the closed set ==================
    print("set-property.py")
    V = TD / "sp"
    rooms(V)
    proj = write(V, "04 Inner World/My Life/Projects/Alpha.md",
                 "---\ntype: project\nstatus: active\ngoal: \"[[G]]\"\n---\nbody\n")
    r = sp(V, str(proj), "focus_rank", "1")
    check("focus_rank 1 is written",
          r.returncode == 0 and "focus_rank: 1" in proj.read_text(encoding="utf-8"),
          r.stderr + proj.read_text(encoding="utf-8"))
    r = sp(V, str(proj), "focus_rank", "4")
    check("focus_rank 4 is refused, and the note is unchanged",
          r.returncode == 1 and "focus_rank: 1" in proj.read_text(encoding="utf-8"),
          r.stderr)
    r = sp(V, str(proj), "focus_rank", "0")
    check("focus_rank 0 is refused: absence is how a project leaves focus",
          r.returncode == 1, r.stderr)
    r = sp(V, str(proj), "focus_rank", "2")
    check("an existing focus_rank is replaced in place, once",
          proj.read_text(encoding="utf-8").count("focus_rank:") == 1
          and "focus_rank: 2" in proj.read_text(encoding="utf-8"),
          proj.read_text(encoding="utf-8"))
    check("the body is untouched", proj.read_text(encoding="utf-8").endswith("body\n"),
          proj.read_text(encoding="utf-8"))
    r = sp(V, str(proj), "focus_rank", "--unset")
    check("--unset removes the line",
          "focus_rank" not in proj.read_text(encoding="utf-8"), r.stderr)
    r = sp(V, str(proj), "external_id", "123456")
    check("a source-owned field is refused", r.returncode == 1, r.stderr)
    r = sp(V, str(proj), "focus_rank", "1", "--dry")
    check("--dry writes nothing",
          "focus_rank" not in proj.read_text(encoding="utf-8"), r.stdout)

    crlf_proj = V / "04 Inner World/My Life/Projects/Beta.md"
    crlf_proj.write_bytes(b"---\r\ntype: project\r\nstatus: active\r\n---\r\nbody\r\n")
    sp(V, str(crlf_proj), "focus_rank", "3")
    raw = crlf_proj.read_bytes()
    check("set-property preserves CRLF byte for byte",
          raw.count(b"\n") == raw.count(b"\r\n") and b"focus_rank: 3" in raw,
          str(raw))


    # === case group 17: the two LOW follow-ups ===========================
    # Vex F5 and the temp-file leak on the dest-symlink refusal.
    print("symlinked notes and the refusal path")
    if not can_symlink():
        skip_symlink_case("F5: a symlinked note in a room is never read")
        skip_symlink_case("F5: a symlinked journal entry is not counted as today's")
        skip_symlink_case("a symlinked destination refuses, exit 1")
    else:
        V = TD / "symlink-note"
        rooms(V)
        smuggled = outside / "smuggled-goal.md"
        smuggled.write_text("---\ntype: goal\nname: Text from outside the vault\n"
                            "status: not-achieved\n---\nbody\n", encoding="utf-8")
        os.symlink(smuggled, V / "04 Inner World/My Life/Goals/Innocent.md")
        write(V, "04 Inner World/My Life/Goals/Real.md",
              "---\ntype: goal\nname: A real goal\nstatus: not-achieved\n---\n")
        rep, r = snap(V)
        names = [g["name"] for g in rep["goals"]["open"]]
        check("F5: a symlinked note in a room is never read",
              names == ["A real goal"], str(names))
        check("F5: and its text reaches neither the JSON nor the brief",
              "outside the vault" not in json.dumps(rep), "it did")

        V = TD / "symlink-journal"
        rooms(V)
        d = TODAY.isoformat()
        month = V / "04 Inner World/Journal" / d[:4] / d[5:7]
        month.mkdir(parents=True, exist_ok=True)
        os.symlink(smuggled, month / ("%s-smuggled.md" % d))
        rep, r = snap(V)
        check("F5: a symlinked journal entry is not counted as today's",
              rep["today"]["journal_entries"] == [],
              str(rep["today"]["journal_entries"]))

        V = TD / "dest-symlink"
        rooms(V)
        victim = outside / "victim-dest.txt"
        victim.write_text("untouched\n", encoding="utf-8")
        (V / ".icor-for-life/scripts").mkdir(parents=True, exist_ok=True)
        os.symlink(victim, V / ".icor-for-life/scripts/snapshot.json")
        r = run(V, "--write")
        leftovers = [f.name for f in (V / ".icor-for-life/scripts").iterdir()
                     if f.name.endswith(".tmp")]
        check("a symlinked destination refuses, exit 1", r.returncode == 1, r.stderr)
        check("and the target is untouched",
              victim.read_text(encoding="utf-8") == "untouched\n",
              victim.read_text(encoding="utf-8")[:40])
        check("and the refusal leaves no .tmp behind", leftovers == [],
              str(leftovers))

    if BREAK:
        check("DELIBERATE: a session-log mention must score (it must not)",
              "Topic C" in allranked, "the suite is proving it can go red")

print()
if fails:
    print("FAIL %d of %d cases" % (len(fails), checks), file=sys.stderr)
    for f in fails:
        print("  " + f, file=sys.stderr)
    sys.exit(1)
# The skip count rides on the summary line, never off it: a run that could not
# plant a symlink proved six fewer things and has to say so where the result is
# read, not only where it happened.
print("OK %d cases held%s"
      % (checks, ", %d skipped (%s)" % (len(skipped), _symlink_why)
         if skipped else ""))
sys.exit(0)
