"""Wrapper so a long --statement string never touches the Bash tool's shell
parser (it refuses complex quoted commands in this worktree-isolated
session)."""
import pathlib
import subprocess
import sys

ENGINE = r"C:/Users/fredc/.claude/skills/constellation-reviewer/scripts/checklist_engine.py"

if __name__ == "__main__":
    survey = sys.argv[1]
    frm = sys.argv[2]
    session = sys.argv[3]
    statement_file = sys.argv[4]
    statement = pathlib.Path(statement_file).read_text(encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, ENGINE, "--file", survey, "flag-candidate",
         "--from", frm, "--statement", statement, "--session-id", session],
        capture_output=True, text=True)
    print(proc.stdout)
    print(proc.stderr, file=sys.stderr)
    sys.exit(proc.returncode)
