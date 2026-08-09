#!/usr/bin/env python
"""g6 re-review, question A (bonus fourth disable point): break the
persistence of span_hash onto the emitted "anchored" statement in
Extractor.anchor() -- the hash is still computed and still lands in
self.anchor_hashes (so THIS run's own new_hashes is fine), but never lands
in the `d` field written to statements.jsonl, so no SUBSEQUENT run can ever
see a previous hash for any slug. Distinct from the team-lead's
"span_hash always returns a constant" attack, which breaks the hash
computation itself rather than its persistence.

Predicts, before running: everything that depends on cross-run comparison
goes red (all 6 StaleAnchorExtractionTests, including
test_stale_tag_span_hash_is_persisted_on_every_anchored_statement, which
asserts span_hash is directly IN `d`; all 5 StaleAnchorRenderReportTests).
The 3 SpanHashUnitTests (call span_hash() directly, unrelated to emit()) and
the tc7 crash-guard test (asserts behavior on a malformed store, independent
of whether THIS run's own hash gets persisted) stay green.

Run from the worktree root:
    python .agent-work/issue-456/evidence/g6-rereview-persistence-attack.py
"""
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
EXTRACT = REPO / "scripts" / "code_map" / "extract.py"

ANCHOR_TEXT = '                          d={"span_hash": h})'
MUTATED_TEXT = '                          d={})  # DISABLE-ATTACK (persistence)'

SELECTOR_CMD = [sys.executable, "-m", "pytest", "tests/test_code_map.py",
                "-k", "stale_tag", "-q", "--tb=no", "-rA", "--color=no"]


def run_selector():
    return subprocess.run(SELECTOR_CMD, cwd=REPO, capture_output=True, text=True)


def outcomes(proc):
    result = {}
    for line in proc.stdout.splitlines():
        line = line.strip()
        if line.startswith("PASSED ") or line.startswith("FAILED "):
            status, test_id = line.split(" ", 1)
            name = test_id.split("::")[-1].split(" ")[0]
            result[name] = status
    return result


EXPECTED_GREEN = {
    "test_stale_tag_hash_is_unchanged_by_pure_reformatting",
    "test_stale_tag_hash_is_unchanged_by_a_docstring_only_edit",
    "test_stale_tag_hash_changes_on_a_real_body_change",
    "test_stale_tag_extract_survives_a_truncated_previous_store",
}


def main():
    original = EXTRACT.read_text(encoding="utf-8")
    if original.count(ANCHOR_TEXT) != 1:
        raise SystemExit("ANCHOR TEXT NOT FOUND exactly once -- extract.py has moved")
    mutated = original.replace(ANCHOR_TEXT, MUTATED_TEXT)
    if mutated.count(MUTATED_TEXT) != 1:
        raise SystemExit("MUTATION did not apply exactly once")

    try:
        EXTRACT.write_text(mutated, encoding="utf-8", newline="\n")
        attack = run_selector()
        attack_outcomes = outcomes(attack)
    finally:
        EXTRACT.write_text(original, encoding="utf-8", newline="\n")

    # Content-normalized clean check (see g6-rereview-render-interception-attack.py
    # for why `git diff --quiet` is used instead of `git status --porcelain`).
    diff_quiet = subprocess.run(
        ["git", "diff", "--quiet", "--", "scripts/code_map/extract.py"], cwd=REPO)
    revert_clean = diff_quiet.returncode == 0

    after = run_selector()
    after_outcomes = outcomes(after)

    actual_green = {t for t, s in attack_outcomes.items() if s == "PASSED"}
    # test_stale_tag_span_hash_is_persisted_on_every_anchored_statement uses
    # subTest, so its own failures may not show as a top-level FAILED line
    # under pytest-subtests; treat "not explicitly PASSED nor FAILED" the
    # same as "did not survive cleanly" for this one name.
    unexpected_green = EXPECTED_GREEN - actual_green
    all_named = set(attack_outcomes)
    after_all_expected_green = all(
        after_outcomes.get(t) == "PASSED" for t in EXPECTED_GREEN)

    summary = {
        "expected_green": sorted(EXPECTED_GREEN),
        "actual_green": sorted(actual_green & all_named),
        "unexpected_green_missing": sorted(unexpected_green),
        "attack_exit": attack.returncode,
        "revert_clean": revert_clean,
        "after_all_expected_green": after_all_expected_green,
    }
    print(summary)

    ok = (not unexpected_green) and revert_clean and after_all_expected_green
    if not ok:
        print("FAIL: prediction did not match observed behavior -- see summary above")
    else:
        print("PASS: the 3 span_hash unit tests and the crash-guard test stayed "
              "green as predicted (correctly orthogonal); extract.py reverted "
              "clean; selector green again")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
