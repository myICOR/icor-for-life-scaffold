#!/usr/bin/env python3
"""Open a vault file in Obsidian, in a new tab.

GL-1005: opening files is deterministic, so a script does it. Used by the
WS-1003 guided tour (and any agent that wants to put a note in front of
the user).

Usage:
    python3 open-in-obsidian.py "path/inside/vault.md" [more paths ...]
    python3 open-in-obsidian.py --dry-run "path.md"   # print, don't open

Resolution order:
  1. The official Obsidian CLI (`obsidian open path=... newtab`) - the
     preferred path; opens in a new tab without stealing focus rules.
  2. The obsidian:// URI, handed to the OS: `os.startfile` on Windows,
     `open` on macOS, `xdg-open` on Linux - works everywhere Obsidian is
     installed, but cannot force a new tab. When this fallback is used,
     stdout carries a RECOMMEND line: suggest the official Obsidian CLI
     to the user (Obsidian installer 1.12.7+, https://help.obsidian.md/cli).

Exit codes: 0 opened (or dry-run) - 2 file not in the vault - 3 no way
to open Obsidian found.
"""
import os
import pathlib
import shutil
import subprocess
import sys
import urllib.parse

ROOT = pathlib.Path(__file__).resolve().parents[2]
VAULT = ROOT.name
WINDOWS = sys.platform == "win32"

# The CLI's names and the places Windows puts it. `obsidian` is what macOS and
# Linux install on PATH. On Windows the executable is `Obsidian.com` and it is
# NOT on PATH until the member turns the CLI on in Settings, so looking only at
# PATH reported "no Obsidian CLI" on every Windows machine (Ian Slattery,
# T11-2). The two install roots below are where the installer puts it.
CLI_NAMES = ("obsidian", "Obsidian.com", "obsidian.exe")


def find_cli():
    """The Obsidian CLI executable, or None. PATH first, then the Windows
    install roots, because the CLI ships there whether or not it is exposed."""
    for name in CLI_NAMES:
        hit = shutil.which(name)
        if hit:
            return hit
    roots = [os.environ.get("LOCALAPPDATA"), os.environ.get("PROGRAMFILES"),
             os.environ.get("PROGRAMFILES(X86)")]
    for base in [r for r in roots if r]:
        for name in CLI_NAMES:
            cand = pathlib.Path(base) / "Obsidian" / name
            if cand.is_file():
                return str(cand)
    return None


def open_one(rel: str, dry: bool) -> int:
    target = ROOT / rel
    if not target.exists():
        print(f"FAIL not in the vault: {rel}", file=sys.stderr)
        return 2

    cli = find_cli()
    if cli:
        cmd = [cli, f"vault={VAULT}", "open", f"path={rel}", "newtab"]
        if dry:
            print("DRY", " ".join(cmd))
            return 0
        run = subprocess.run(cmd, capture_output=True, text=True)
        if run.returncode == 0:
            print(f"OK opened via CLI: {rel}")
            return 0
        print(f"note: CLI failed ({run.stderr.strip() or run.returncode}), falling back to URI", file=sys.stderr)

    uri = ("obsidian://open?vault=" + urllib.parse.quote(VAULT)
           + "&file=" + urllib.parse.quote(rel))

    # Windows has no `open` and no `xdg-open`, so the URI branch found no
    # opener and every stop of the WS-1003 guided tour failed with exit 3. The
    # OS handler for a protocol URI on Windows is os.startfile, which is a
    # Python builtin rather than a command, so it gets its own branch and it
    # also has to be the branch --dry-run prints (Ian Slattery, T11-1).
    if WINDOWS:
        if dry:
            print("DRY os.startfile", uri)
        else:
            try:
                os.startfile(uri)               # noqa: S606 - the OS handler
            except OSError as exc:
                print(f"FAIL Windows could not open the obsidian:// URI ({exc}); "
                      "is Obsidian installed?", file=sys.stderr)
                return 3
            print(f"OK opened via URI: {rel}")
    else:
        opener = shutil.which("open") or shutil.which("xdg-open")
        if not opener:
            print("FAIL no Obsidian CLI and no OS opener found", file=sys.stderr)
            return 3
        if dry:
            print("DRY", opener, uri)
        else:
            subprocess.run([opener, uri], check=False)
            print(f"OK opened via URI: {rel}")

    # "Obsidian 1.12+" was wrong on every platform: the CLI arrived with
    # INSTALLER 1.12.7, and the installer version is not the app version the
    # member reads in Settings (Ian Slattery, T11-3).
    print("RECOMMEND the official Obsidian CLI was not found - suggest it to "
          "the user (Obsidian installer 1.12.7+ ships it; see "
          "https://help.obsidian.md/cli) so tours can open files in new tabs."
          + (" On Windows it is Obsidian.com and it stays off PATH until the "
             "member turns the CLI on in Settings." if WINDOWS else ""))
    return 0


def main() -> int:
    args = [a for a in sys.argv[1:] if a != "--dry-run"]
    dry = "--dry-run" in sys.argv[1:]
    if not args:
        print(__doc__)
        return 2
    worst = 0
    for rel in args:
        worst = max(worst, open_one(rel, dry))
    return worst


if __name__ == "__main__":
    sys.exit(main())
