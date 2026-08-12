"""Baseline the constellation-skills test files this plan will touch.

Uses the pinned pythoncore interpreter (the Bash-tool `py` is the codex runtime,
which has no pytest). Read-only: runs tests, changes nothing.
"""
import subprocess, sys

PY = r"C:\Users\fredc\AppData\Local\Python\pythoncore-3.14-64\python.exe"
ROOT = r"C:\Programs\constellation-skills"
TESTS = ["tests/test_crew_launcher.py", "tests/test_verify_agent_feedback.py",
         "tests/test_install_constellation.py", "tests/test_agent_work_root.py"]

cmd = [PY, "-m", "pytest", *TESTS, "-q"]
print("cwd:", ROOT)
print("cmd:", " ".join(cmd))
r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
print((r.stdout or "").strip()[-1500:])
print((r.stderr or "").strip()[-600:])
print("exit:", r.returncode)
sys.exit(0)
