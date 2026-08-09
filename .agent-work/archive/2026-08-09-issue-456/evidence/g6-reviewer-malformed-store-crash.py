"""g6 review, "Also verify" item 2: read-before-overwrite robustness. Reproduces
a genuine, previously-unreported crash: a truncated/malformed leftover
statements.jsonl (simulating an interrupted prior extraction -- a real
scenario, since extract.run()'s writer has no atomic rename) makes every
subsequent `extract` fail with an uncaught JSONDecodeError instead of treating
the unreadable store as absent."""
import tempfile
import subprocess
import sys
import os
import shutil
from pathlib import Path

sys.path.insert(0, ".")
from tests.test_code_map import _make_anchor_repo

tmp = tempfile.mkdtemp(prefix="g6-review-malformed-")
repo = Path(tmp)
_make_anchor_repo(repo)
artifacts = repo / ".code-map"
os.makedirs(artifacts, exist_ok=True)

# First a real extraction so the file has the expected anchored-rows shape.
r = subprocess.run([sys.executable, "-m", "scripts.code_map", "extract",
                    "--root", str(repo), "--artifacts", str(artifacts)],
                   capture_output=True, text=True)
print("initial extract exit:", r.returncode)

# Corrupt statements.jsonl: truncate the last line mid-JSON, simulating a
# process killed mid-write (extract.run()'s own writer is a plain
# `with open(outp, "w")`, no atomic rename).
stp = artifacts / "statements.jsonl"
data = stp.read_text(encoding="utf-8")
lines = data.splitlines()
lines[-1] = lines[-1][: len(lines[-1]) // 2]
stp.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")

r2 = subprocess.run([sys.executable, "-m", "scripts.code_map", "extract",
                     "--root", str(repo), "--artifacts", str(artifacts)],
                    capture_output=True, text=True)
print("second extract (against truncated store) exit:", r2.returncode)
print("STDOUT tail:", r2.stdout[-300:])
print("STDERR tail:", r2.stderr[-800:])

shutil.rmtree(tmp, ignore_errors=True)
