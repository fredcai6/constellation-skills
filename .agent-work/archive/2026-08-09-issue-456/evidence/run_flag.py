import pathlib
import subprocess
import sys

ENGINE = r"C:/Users/fredc/.claude/skills/constellation-reviewer/scripts/checklist_engine.py"

if __name__ == "__main__":
    survey, frm, session, stmt_file = sys.argv[1:5]
    statement = pathlib.Path(stmt_file).read_text(encoding="utf-8").strip()
    proc = subprocess.run(
        [sys.executable, ENGINE, "--file", survey, "flag-candidate",
         "--from", frm, "--statement", statement, "--session-id", session],
        capture_output=True, text=True)
    print(proc.stdout)
    print(proc.stderr, file=sys.stderr)
    sys.exit(proc.returncode)
