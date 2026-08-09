"""g6 re-review, question C: does tc7's guard fail safe or fail silent, and
does it catch ONLY the parse failure rather than swallowing unrelated errors?
Attack: make statements.jsonl a DIRECTORY instead of a file, so open() raises
an OS-level error (PermissionError on Windows; IsADirectoryError on POSIX) --
NOT one of the three caught types (JSONDecodeError, UnicodeDecodeError,
KeyError). Prediction: this should propagate and crash, proving the guard is
scoped to parse failures only, not a blanket swallow of anything that goes
wrong reading the previous store.
"""
import tempfile
import subprocess
import sys
import os
import shutil
from pathlib import Path

sys.path.insert(0, ".")
from tests.test_code_map import _make_anchor_repo

tmp = tempfile.mkdtemp(prefix="g6-rereview-scope-")
repo = Path(tmp)
_make_anchor_repo(repo)
artifacts = repo / ".code-map"
os.makedirs(artifacts, exist_ok=True)

# Make statements.jsonl a DIRECTORY, not a file -- an unrelated OS-level
# error, not a parse failure.
(artifacts / "statements.jsonl").mkdir()

r = subprocess.run([sys.executable, "-m", "scripts.code_map", "extract",
                    "--root", str(repo), "--artifacts", str(artifacts)],
                   capture_output=True, text=True)
print("extract against a DIRECTORY named statements.jsonl -- exit:", r.returncode)
print("STDOUT tail:", r.stdout[-200:])
print("STDERR tail (should show an uncaught OS-level error, NOT swallowed):",
      r.stderr[-500:])

crashed_visibly = r.returncode != 0 and "unreadable" not in r.stdout
print()
print("PASS: guard did not swallow an unrelated OS-level error" if crashed_visibly
      else "FAIL: guard swallowed an error it should not have caught")

shutil.rmtree(tmp, ignore_errors=True)
