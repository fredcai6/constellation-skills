"""C10 — the fall from the 3204 baseline, derived mechanically, test by test.

The handoff: "Deleting the engine implementation removes its half of the
parametrized table, so expect the passed count to fall. State the new number and
account for the difference test by test — a drop you cannot explain is a stop
condition." And: derive the difference from collected counts, not from a glance
at the tail.

So this asserts an identity rather than a number:

    baseline_passed - after_passed  ==  before_collected - after_collected

where the collected counts are `--collect-only` on
`tests/test_worktree_derivation.py` before and after the change, and it ALSO
re-collects the WHOLE suite now and checks that total against the baseline
total. The second half is what rules out "some other file also lost tests" --
without it the identity above could hold by coincidence of two errors.

Skips and failures must be unchanged: a fall in `passed` that is really a rise
in `skipped` is not the accounted-for difference.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

BASELINE = HERE / "b0-baseline-suite.txt"
AFTER = HERE / "m6-full-suite.txt"
COLLECT_BEFORE = HERE / "b1-collect-before.txt"
COLLECT_AFTER = HERE / "b2-collect-after.txt"

# The per-test accounting, stated up front and asserted below. Deleting the
# "engine" entry from IMPLEMENTATIONS removes one parametrization of three
# tests, and the two-copies drift test goes with the second copy.
EXPECTED_BREAKDOWN = [
    ("test_derivation[engine-*]", 16),                # 16 cases x 1 implementation
    ("test_the_two_copies_agree[*]", 16),             # the whole drift test
    ("test_derivation_is_lexical_not_realpath[engine]", 1),
    ("test_derivation_never_raises[engine]", 1),
]


def counts(path: Path) -> dict[str, int]:
    text = path.read_text(encoding="utf-8")
    out = {}
    for key in ("passed", "skipped", "failed", "error"):
        m = re.search(rf"(\d+) {key}", text)
        out[key] = int(m.group(1)) if m else 0
    return out


def collected(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    m = re.search(r"(\d+) tests collected", text)
    if not m:
        raise SystemExit(f"no collected count in {path}")
    return int(m.group(1))


def collect_whole_suite() -> int:
    out = subprocess.run(
        ["env", "-u", "SPINE_FILE", "-u", "SPINE_SESSION", "-u", "SPINE_PARENT",
         "-u", "CREW_SCRATCH_DIR", "py", "-m", "pytest", "-q", "--collect-only"],
        cwd=ROOT, capture_output=True, text=True)
    m = re.search(r"(\d+) tests collected", out.stdout)
    if not m:
        raise SystemExit("could not collect the whole suite")
    return int(m.group(1))


def main() -> int:
    base, after = counts(BASELINE), counts(AFTER)
    before_c, after_c = collected(COLLECT_BEFORE), collected(COLLECT_AFTER)
    failures: list[str] = []

    print(f"baseline (pre-change, this tree): {base}")
    print(f"after   (post-change, this tree): {after}")
    print(f"tests/test_worktree_derivation.py collected: {before_c} -> {after_c} "
          f"(delta {before_c - after_c})")

    expected_drop = sum(n for _, n in EXPECTED_BREAKDOWN)
    print("\naccounting, test by test:")
    for name, n in EXPECTED_BREAKDOWN:
        print(f"  -{n:>3}  {name}")
    print(f"  ----  expected drop: {expected_drop}")

    if before_c - after_c != expected_drop:
        failures.append(f"collected delta {before_c - after_c} != the {expected_drop} "
                        f"accounted for test by test")
    if base["passed"] - after["passed"] != before_c - after_c:
        failures.append(f"suite fell by {base['passed'] - after['passed']}, but the one "
                        f"changed file only lost {before_c - after_c} tests")
    for key in ("skipped", "failed", "error"):
        if base[key] != after[key]:
            failures.append(f"{key} changed: {base[key]} -> {after[key]}")
    if after["failed"] or after["error"]:
        failures.append("the suite is not green")

    # The independent half: no OTHER file changed its collected count.
    whole = collect_whole_suite()
    expected_whole = base["passed"] + base["skipped"] - expected_drop
    print(f"\nwhole-suite collection now: {whole}; baseline collected "
          f"{base['passed'] + base['skipped']} - {expected_drop} = {expected_whole}")
    if whole != expected_whole:
        failures.append(f"whole-suite collection is {whole}, expected {expected_whole} "
                        f"— some other file changed its test count")

    if failures:
        for line in failures:
            print(f"FAIL: {line}", file=sys.stderr)
        return 1
    print(f"\nOK: {base['passed']} -> {after['passed']} passed, and every one of the "
          f"{expected_drop} lost tests is accounted for.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
