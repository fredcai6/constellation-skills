"""Wrapper so a long --finding string never touches the Bash tool's shell
parser (it refuses complex quoted commands in this worktree-isolated
session)."""
import pathlib
import subprocess
import sys

ENGINE = r"C:/Users/fredc/.claude/skills/constellation-reviewer/scripts/checklist_engine.py"

if __name__ == "__main__":
    survey = sys.argv[1]
    item_id = sys.argv[2]
    result = sys.argv[3]
    session = sys.argv[4]
    finding_file = sys.argv[5]
    finding = pathlib.Path(finding_file).read_text(encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, ENGINE, "--file", survey, "record", item_id,
         "--result", result, "--finding", finding, "--session-id", session],
        capture_output=True, text=True)
    print(proc.stdout)
    print(proc.stderr, file=sys.stderr)
    sys.exit(proc.returncode)
