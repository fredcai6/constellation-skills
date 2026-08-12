"""Throwaway probe for g1-review's mutation M4: widen RESTATE_ALLOWED_FIELDS with an
`original` key and have the applier prefer op["original"] over the parsed statement --
the evidence-destruction hole the op exists to close.

Runs the mutation TWICE against the same broken writer:

  1. with Rework 1's three new tests deselected -- reproduces the reviewer's finding
     (GREEN, 21 passed, exit 0: the pre-rework suite did not notice);
  2. with the whole class -- must be RED (the pin catches it).

Exits 0 only if both hold. Restores the source byte-for-byte either way."""

import io
import subprocess
import sys
from pathlib import Path

SRC = Path("scripts/apply_episode_delta.py")
ORIGINAL = io.open(SRC, encoding="utf-8", newline="").read()
EOL = "\r\n" if "\r\n" in ORIGINAL else "\n"

CLASS = "tests/test_episode_store.py::RestateAssertionTests"
REWORK1_TESTS = (
    "test_the_op_field_allowlist_is_pinned_to_its_exact_membership",
    "test_no_field_on_the_op_can_supply_the_original_statement",
    "test_the_quoted_original_is_exactly_the_statement_that_was_on_disk",
)

M4 = (
    (
        'RESTATE_ALLOWED_FIELDS = ("op", "id", "assertion", "statement", "history")',
        'RESTATE_ALLOWED_FIELDS = ("op", "id", "assertion", "statement", "history", "original")',
    ),
    (
        "    original_statement = assertion.statement\n",
        '    original_statement = op.get("original", assertion.statement)\n',
    ),
)


def run(*extra):
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", CLASS, *extra],
        capture_output=True, text=True,
    )
    tail = proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else "(no output)"
    return proc.returncode, tail


ok = True
try:
    mutated = ORIGINAL
    for old, new in M4:
        old, new = old.replace("\n", EOL), new.replace("\n", EOL)
        assert mutated.count(old) == 1, f"M4 anchor matched {mutated.count(old)} times: {old!r}"
        mutated = mutated.replace(old, new)
    assert mutated != ORIGINAL
    io.open(SRC, "w", encoding="utf-8", newline="").write(mutated)

    deselect = []
    for name in REWORK1_TESTS:
        deselect += ["--deselect", f"{CLASS}::{name}"]

    rc_before, tail_before = run(*deselect)
    verdict = "GREEN - the reviewer's finding, reproduced" if rc_before == 0 else "RED (unexpected)"
    print(f"M4 vs the PRE-rework suite (3 new tests deselected): exit={rc_before} "
          f"{verdict} :: {tail_before}", flush=True)
    ok = ok and rc_before == 0

    rc_after, tail_after = run()
    verdict = "RED - the pin catches it" if rc_after != 0 else "GREEN (VACUOUS!)"
    print(f"M4 vs the POST-rework suite (all tests): exit={rc_after} "
          f"{verdict} :: {tail_after}", flush=True)
    ok = ok and rc_after != 0

    # Name what actually broke, so the claim is "these tests caught it", not a bare count.
    failing = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "--no-header", "-rf", CLASS],
        capture_output=True, text=True,
    ).stdout
    for line in failing.splitlines():
        if line.startswith("FAILED") or line.startswith("SUBFAIL"):
            print("  " + line.strip(), flush=True)
finally:
    io.open(SRC, "w", encoding="utf-8", newline="").write(ORIGINAL)
    restored = io.open(SRC, encoding="utf-8", newline="").read() == ORIGINAL
    print("restored byte-for-byte:", restored, flush=True)
    ok = ok and restored

print("M4 probe:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
