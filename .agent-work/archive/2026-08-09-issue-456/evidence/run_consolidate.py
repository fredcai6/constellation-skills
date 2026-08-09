import pathlib
import subprocess
import sys

ENGINE = r"C:/Users/fredc/.claude/skills/constellation-reviewer/scripts/checklist_engine.py"

if __name__ == "__main__":
    survey, verdict, session, summary_file = sys.argv[1:5]
    summary = pathlib.Path(summary_file).read_text(encoding="utf-8").strip()
    proc = subprocess.run(
        [sys.executable, ENGINE, "--file", survey, "consolidate",
         "--verdict", verdict, "--summary", summary, "--session-id", session],
        capture_output=True, text=True)
    print(proc.stdout)
    print(proc.stderr, file=sys.stderr)
    sys.exit(proc.returncode)
