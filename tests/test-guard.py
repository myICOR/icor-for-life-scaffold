"""The top folder stays clear: Claude Code's hook (guard-paths.py) and the tools' shared writer refuse it. Stdlib only."""
import importlib.util, json, subprocess, sys, tempfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
GUARD = ROOT / "_System/Tools/guard-paths.py"
fails, n = [], 0


def check(cond, msg):
    global n
    n += 1
    if not cond:
        fails.append(msg)


def hook(path, cwd):
    r = subprocess.run([sys.executable, "-B", str(GUARD)], input=json.dumps({"tool_name": "Write", "tool_input": {"file_path": path}, "cwd": str(cwd)}),
                       capture_output=True, text=True)
    return r.returncode, r.stderr


with tempfile.TemporaryDirectory() as tmp:
    v = Path(tmp) / "ICOR for Life"
    (v / "_System").mkdir(parents=True)
    (v / "_System/schema.json").write_text((ROOT / "_System/schema.json").read_text())
    for room in json.loads((ROOT / "_System/schema.json").read_text())["rooms"]:
        (v / room).mkdir()
    refused = {"CleanShot 2026-11-21 at 00.30.03@2x.png": "05 Assets/Images/", "memo.m4a": "05 Assets/Audio/",
               "Invoice.pdf": "05 Assets/Documents/", "Untitled.md": "01 Inbox", "board.canvas": "01 Inbox/", "Random/thing.md": "01 Inbox"}
    for rel, home in refused.items():
        code, msg = hook(str(v / rel), v)
        check(code == 2, f"hook lets {rel} through")
        check(home in msg and "AGENTS.md" in msg, f"hook message for {rel} does not name {home} and AGENTS.md: {msg!r}")
    allowed = ["README.md", "AGENTS.md", "CLAUDE.md", ".gitignore", "04 Inner World/Notes/A note.md", "04 Inner World/Journal/2026/11/2026-11-21_x.md",
               "00 Daily Scratchpad/2026/11/2026-11-21.md", "05 Assets/Images/shot.png", "01 Inbox/x.md", "_System/Templates/tool.md",
               ".claude/skills/capture/SKILL.md", ".agents/skills/capture/SKILL.md", ".icor-for-life/scripts/quality.json", "06 AI Team/x.md"]
    for rel in allowed:
        code, msg = hook(str(v / rel), v)
        check(code == 0, f"hook refuses {rel}: {msg}")
    code, _ = hook("04 Inner World/Notes/relative.md", v)
    check(code == 0, "hook refuses a relative path inside a room")
    code, _ = hook("stray.png", v)
    check(code == 2, "hook lets a relative top-level path through")
    code, _ = hook(str(Path(tmp) / "outside.md"), v)
    check(code == 0, "hook refuses a path outside the folder")
    # the tools' shared writer
    spec = importlib.util.spec_from_file_location("noteio", ROOT / "_System/Tools/noteio-icor.py")
    nio = importlib.util.module_from_spec(spec); spec.loader.exec_module(nio)
    try:
        nio.write_note(v / "stray.md", "x"); check(False, "write_note wrote in the top folder")
    except SystemExit as e:
        check("top folder" in str(e) and not (v / "stray.md").exists(), "write_note's refusal is unclear or it wrote anyway")
    nio.write_note(v / "01 Inbox/fine.md", "x")
    check((v / "01 Inbox/fine.md").read_text() == "x", "write_note no longer writes inside a room")

# the hook is wired for Claude Code
s = json.loads((ROOT / ".claude/settings.json").read_text())
cmds = [h["command"] for e in s["hooks"]["PreToolUse"] for h in e["hooks"] if "Write" in e["matcher"] and "Edit" in e["matcher"]]
check(any("guard-paths.py" in c and "$CLAUDE_PROJECT_DIR" in c for c in cmds), ".claude/settings.json does not run guard-paths.py on Write and Edit")
check("## Where files go" in (ROOT / "AGENTS.md").read_text() and "Never write in the top folder" in (ROOT / "AGENTS.md").read_text(), "AGENTS.md lacks the rule")
for sk in ("capture", "new-object"):
    check("top folder" in (ROOT / f"_System/Skills/{sk}/SKILL.md").read_text(), f"skill {sk} does not say where files go")

if fails:
    print("\n".join("FAIL " + f for f in fails)); sys.exit(1)
print(f"OK {n} cases held")
