#!/usr/bin/env python
"""Mechanical disable-attack acceptance test for the g6 remediation (issue #456).

Reproduces the g6 reviewer's attack exactly: force `stale = []` immediately
after the real staleness computation in scripts/code_map/extract.py's
run(), rerun the closing `stale_tag` selector, and assert that every one of
the five named "does not flag" tests -- the ones the reviewer found vacuous
-- is now in the FAILED set. Restores extract.py in a `finally` block (even
on assertion failure), re-confirms a clean `git status` on that file, and
reruns the selector once more to confirm it is green again.

Exit 0 only if every one of those checks holds. Prints a summary dict
either way so the run is self-describing, not just pass/fail.

Run from the worktree root:
    python .agent-work/issue-456/evidence/g6_disable_attack.py
"""
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
EXTRACT = REPO / "scripts" / "code_map" / "extract.py"

ANCHOR_TEXT = "stale = sorted(slug for slug, meta in new_hashes.items()"
MUTATION_COMMENT = ("  # DISABLE-ATTACK: forces the gate off on this code "
                     "path (g6_disable_attack.py)")

NAMED_TESTS = [
    "test_stale_tag_first_extraction_flags_nothing",
    "test_stale_tag_does_not_flag_a_reformat_across_two_extractions",
    "test_stale_tag_does_not_flag_an_unrelated_anchor",
    "test_stale_tag_render_report_does_not_flag_a_reformat",
    "test_stale_tag_render_report_does_not_fail_the_build",
]

SELECTOR_CMD = [sys.executable, "-m", "pytest", "tests/test_code_map.py",
                "-k", "stale_tag", "-q", "--tb=no", "-rA", "--color=no"]


def run_selector():
    return subprocess.run(SELECTOR_CMD, cwd=REPO, capture_output=True, text=True)


def outcomes(proc):
    """Parse pytest's `-rA` short summary section into {test_name: PASSED|FAILED}."""
    result = {}
    for line in proc.stdout.splitlines():
        line = line.strip()
        if line.startswith("PASSED ") or line.startswith("FAILED "):
            status, test_id = line.split(" ", 1)
            # test_id looks like "tests/test_code_map.py::Class::test_name" or
            # "...::test_name - AssertionError: ..." for FAILED lines.
            name = test_id.split("::")[-1].split(" ")[0]
            result[name] = status
    return result


def mutate(original: str) -> str:
    lines = original.splitlines(keepends=True)
    idx = None
    for i, line in enumerate(lines):
        if ANCHOR_TEXT in line:
            idx = i
            break
    if idx is None:
        raise SystemExit("ANCHOR TEXT NOT FOUND in extract.py -- run() has "
                          "moved; update ANCHOR_TEXT in this script")
    indent = line[:len(line) - len(line.lstrip(" "))]
    # The anchor assignment spans two lines (the sorted(...) call and its
    # continuation); insert the override right after both.
    insert_at = idx + 2
    mutation_line = indent + "stale = []" + MUTATION_COMMENT + "\n"
    mutated_lines = lines[:insert_at] + [mutation_line] + lines[insert_at:]
    mutated = "".join(mutated_lines)
    # Assert the mutation actually applied -- a check that cannot fail is
    # indistinguishable from one that passed (CREW_CONTEXT.md).
    if mutated.count(MUTATION_COMMENT) != 1:
        raise SystemExit("MUTATION did not apply exactly once (found %d)"
                          % mutated.count(MUTATION_COMMENT))
    return mutated


def main():
    original = EXTRACT.read_text(encoding="utf-8")
    mutated = mutate(original)

    try:
        EXTRACT.write_text(mutated, encoding="utf-8", newline="\n")
        attack = run_selector()
        attack_outcomes = outcomes(attack)
    finally:
        EXTRACT.write_text(original, encoding="utf-8", newline="\n")

    clean = subprocess.run(
        ["git", "status", "--porcelain", "--", "scripts/code_map/extract.py"],
        cwd=REPO, capture_output=True, text=True)
    revert_clean = clean.stdout.strip() == ""

    after = run_selector()
    after_outcomes = outcomes(after)

    survivors = [t for t in NAMED_TESTS if attack_outcomes.get(t) != "FAILED"]
    after_all_green = all(after_outcomes.get(t) == "PASSED" for t in NAMED_TESTS)

    summary = {
        "attack_outcomes": {t: attack_outcomes.get(t, "MISSING") for t in NAMED_TESTS},
        "attack_exit": attack.returncode,
        "survivors": survivors,
        "revert_clean": revert_clean,
        "after_outcomes": {t: after_outcomes.get(t, "MISSING") for t in NAMED_TESTS},
        "after_exit": after.returncode,
        "after_all_named_green": after_all_green,
    }
    print(summary)

    ok = (not survivors) and revert_clean and after_all_green
    if not ok:
        print("FAIL: disable-attack did not fully land -- see summary above")
    else:
        print("PASS: all 5 named tests failed under the disable attack; "
              "extract.py reverted clean; selector green again")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
