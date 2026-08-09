"""Follow-up to mutation C: widen scan_episode() properly.

C removed only the `## Agent-supplied` break and stayed GREEN, because the SECOND
early break (`if episode_id is not None and run is not None: break`) still fires first
on a well-formed record. So C did not actually widen the read.

C2 removes BOTH breaks and echoes every line -- the literal "inject a leak into
scan_episode()" the reviewer handoff asks for, and the direct test of the module
docstring's claim that "anything that widens this function widens the valve".

Restores byte-identically and hash-verifies.
"""
import hashlib
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
TARGET = ROOT / "scripts" / "verify_episode_captured.py"

BREAK1 = (
    b"            if line.startswith(AGENT_SUPPLIED_HEADING):\n"
    b"                break  # statements start here \xe2\x80\x94 stop before reading any of them\n"
)
BREAK1_NEW = (
    b"            print(line, file=sys.stderr)  # REVIEWER-INJECTED LEAK C2\n"
    b"            if False:\n"
    b"                pass\n"
)
BREAK2 = b"            if episode_id is not None and run is not None:\n                break\n"
BREAK2_NEW = b"            if False:\n                pass\n"

original = TARGET.read_bytes()
BEFORE = hashlib.sha256(original).hexdigest()
print(f"pre-mutation sha256: {BEFORE}")

for name, anchor in (("break-at-agent-supplied", BREAK1), ("break-when-both-found", BREAK2)):
    if anchor not in original:
        print(f"ANCHOR '{name}' NOT FOUND -- would silently no-op. ABORT.")
        sys.exit(3)

mutated = original.replace(BREAK1, BREAK1_NEW, 1).replace(BREAK2, BREAK2_NEW, 1)
assert mutated != original
TARGET.write_bytes(mutated)
assert b"LEAK C2" in TARGET.read_bytes(), "mutation did not apply"
print("MUTATION APPLIED: both early breaks removed + per-line stderr echo in scan_episode()")

try:
    r = subprocess.run(
        [sys.executable, "-m", "pytest",
         "tests/test_verify_episode_captured.py::ValveTests", "-q"],
        cwd=str(ROOT), capture_output=True, text=True,
        env={**os.environ, "FORCE_COLOR": "0", "NO_COLOR": "1"},
    )
finally:
    TARGET.write_bytes(original)

AFTER = hashlib.sha256(TARGET.read_bytes()).hexdigest()
print(f"RED RUN exit={r.returncode}")
for line in r.stdout.splitlines():
    if line.startswith("FAILED") or " passed" in line or " failed" in line:
        print("  " + line[:150])
print(f"post-restore sha256: {AFTER}")
print(f"RESTORE byte-identical: {AFTER == BEFORE}")
ok = r.returncode != 0 and AFTER == BEFORE
print(f"C2 VALID (widening scan_episode DOES trip the sentinel): {ok}")
sys.exit(0 if ok else 1)
