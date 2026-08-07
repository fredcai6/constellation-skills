"""Reviewer's OWN red proofs of the sentinel valve test.

Three independent mutations, each restored byte-identically and hash-verified:

  A. STDERR leak of every line scan_episode() actually READS (loop body).
     EXPECTED GREEN -- and that is the point: the valve works by never reading
     statement lines at all, so leaking what it reads leaks nothing. Recorded as a
     characterisation, not a failure.
  B. STDERR leak of the whole episode body from matched_episodes(). The implementer's
     own red proof leaked to STDOUT from scan_episode(); this exercises the OTHER half
     of the assertion (stderr) from a DIFFERENT call site.
  C. Widen scan_episode() -- remove both early breaks and echo every line -- which is
     the exact "anything that widens this function widens the valve" claim in the
     module docstring.

B and C MUST go red. A leak test that cannot fail is worth nothing.
"""
import hashlib
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
TARGET = ROOT / "scripts" / "verify_episode_captured.py"

MUTATIONS = {
    "A_leak_what_scan_reads_stderr": (
        b"        for raw in handle:\n",
        b"        for raw in handle:\n"
        b"            print(raw, file=sys.stderr)  # REVIEWER-INJECTED LEAK A\n",
        False,  # expected to stay green
    ),
    "B_leak_whole_body_from_matched_episodes_stderr": (
        b"        scanned += 1\n",
        b"        scanned += 1\n"
        b'        print(path.read_text(encoding="utf-8"), file=sys.stderr)  # LEAK B\n',
        True,
    ),
    "C_widen_scan_episode_remove_breaks": (
        b"            if line.startswith(AGENT_SUPPLIED_HEADING):\n"
        b"                break  # statements start here \xe2\x80\x94 stop before reading any of them\n",
        b"            if False:\n"
        b"                pass\n"
        b"            print(line, file=sys.stderr)  # REVIEWER-INJECTED LEAK C\n",
        True,
    ),
}


def pytest(args):
    env = {**os.environ, "FORCE_COLOR": "0", "NO_COLOR": "1"}
    return subprocess.run(
        [sys.executable, "-m", "pytest", *args],
        cwd=str(ROOT), capture_output=True, text=True, env=env,
    )


original = TARGET.read_bytes()
BEFORE = hashlib.sha256(original).hexdigest()
print(f"pre-mutation sha256: {BEFORE}\n")

verdicts = {}
for label, (anchor, inject, expect_red) in MUTATIONS.items():
    if anchor not in original:
        print(f"[{label}] ANCHOR NOT FOUND -- mutation would silently no-op. ABORT.")
        sys.exit(3)
    mutated = original.replace(anchor, inject, 1)
    assert mutated != original, f"{label}: mutation did not change bytes"
    TARGET.write_bytes(mutated)
    assert TARGET.read_bytes() == mutated, f"{label}: mutation did not apply"
    print(f"[{label}] MUTATION APPLIED (expect_red={expect_red})")
    try:
        # C also breaks the second early-break's reachability guarantee; run the whole
        # valve class either way.
        r = pytest(["tests/test_verify_episode_captured.py::ValveTests", "-q"])
    finally:
        TARGET.write_bytes(original)
        h = hashlib.sha256(TARGET.read_bytes()).hexdigest()
        assert h == BEFORE, f"{label}: RESTORE FAILED ({h})"
    red = r.returncode != 0
    for line in r.stdout.splitlines():
        if line.startswith("FAILED") or " passed" in line or " failed" in line:
            print("      " + line[:150])
    verdicts[label] = (red, expect_red, red == expect_red)
    print(f"      exit={r.returncode} red={red} matches-expectation={red == expect_red}")
    print("      RESTORED byte-identical: True\n")

AFTER = hashlib.sha256(TARGET.read_bytes()).hexdigest()
print(f"post-all-restores sha256: {AFTER}")
print(f"FINAL RESTORE byte-identical: {AFTER == BEFORE}")

green = pytest(["tests/test_verify_episode_captured.py", "-q"])
print(f"GREEN RUN exit={green.returncode}")
for line in green.stdout.splitlines()[-3:]:
    print("  " + line[:150])

ok = all(v[2] for v in verdicts.values()) and AFTER == BEFORE and green.returncode == 0
print(f"\nRED-PROOF SUITE VALID: {ok}")
sys.exit(0 if ok else 1)
