import pathlib
import subprocess
import sys

ENGINE = r"C:/Users/fredc/.claude/skills/constellation-reviewer/scripts/checklist_engine.py"

if __name__ == "__main__":
    survey, item_id, cond, authority, session, reason_file = sys.argv[1:7]
    reason = pathlib.Path(reason_file).read_text(encoding="utf-8").strip()
    proc = subprocess.run(
        [sys.executable, ENGINE, "--file", survey, "waive", item_id,
         "--cond", cond, "--authority", authority, "--reason", reason,
         "--force", "--session-id", session],
        capture_output=True, text=True)
    print(proc.stdout)
    print(proc.stderr, file=sys.stderr)
    sys.exit(proc.returncode)
