#!/usr/bin/env python
"""g6 re-review, question A (third disable point): disable render.py's own
interception of "stale-anchor" statements in load_stores(), leaving
extract.py's emission fully intact. Predicts, before running, that the 6
extract/unit-level tests stay green (correctly orthogonal -- this mutation
is render-only) and all 5 StaleAnchorRenderReportTests go red (render_report
.json's stale_tags can never populate). Restores render.py in a `finally`
block and re-confirms a clean, content-normalized `git diff --quiet`.

Run from the worktree root:
    python .agent-work/issue-456/evidence/g6-rereview-render-interception-attack.py
"""
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
RENDER = REPO / "scripts" / "code_map" / "render.py"

ANCHOR_TEXT = 'if p == "stale-anchor":'
MUTATED_TEXT = 'if p == "stale-anchor" and False:  # DISABLE-ATTACK (render interception)'

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


EXPECTED_RED = {
    "test_stale_tag_render_report_does_not_flag_a_reformat",
    "test_stale_tag_render_report_flags_a_real_body_change",
    "test_stale_tag_render_report_does_not_fail_the_build",
    "test_stale_tag_advisory_line_does_not_begin_with_fail",
    "test_stale_tag_render_report_carries_no_timing_field",
}


def main():
    original = RENDER.read_text(encoding="utf-8")
    if original.count(ANCHOR_TEXT) != 1:
        raise SystemExit("ANCHOR TEXT NOT FOUND exactly once -- render.py has moved")
    mutated = original.replace(ANCHOR_TEXT, MUTATED_TEXT)
    if mutated.count(MUTATED_TEXT) != 1:
        raise SystemExit("MUTATION did not apply exactly once")

    try:
        RENDER.write_text(mutated, encoding="utf-8", newline="\n")
        attack = run_selector()
        attack_outcomes = outcomes(attack)
    finally:
        RENDER.write_text(original, encoding="utf-8", newline="\n")

    # Content-normalized clean check, per CREW_CONTEXT.md ("never compare two
    # files by raw working-tree bytes -- compare normalized content or blob
    # OIDs"): `git diff --quiet` normalizes CRLF/LF the way this repo's own
    # core.autocrlf=true expects, unlike a raw `git status --porcelain` check.
    diff_quiet = subprocess.run(
        ["git", "diff", "--quiet", "--", "scripts/code_map/render.py"], cwd=REPO)
    revert_clean = diff_quiet.returncode == 0

    after = run_selector()
    after_outcomes = outcomes(after)

    actual_red = {t for t, s in attack_outcomes.items() if s == "FAILED"}
    unexpected_green = EXPECTED_RED - actual_red
    unexpected_red = actual_red - EXPECTED_RED
    after_all_green = all(after_outcomes.get(t) == "PASSED" for t in EXPECTED_RED)

    summary = {
        "expected_red": sorted(EXPECTED_RED),
        "actual_red": sorted(actual_red),
        "unexpected_green": sorted(unexpected_green),
        "unexpected_red": sorted(unexpected_red),
        "attack_exit": attack.returncode,
        "revert_clean": revert_clean,
        "after_all_green": after_all_green,
    }
    print(summary)

    ok = (not unexpected_green) and (not unexpected_red) and revert_clean and after_all_green
    if not ok:
        print("FAIL: prediction did not match observed behavior -- see summary above")
    else:
        print("PASS: exactly the predicted 5 render-report tests went red; "
              "render.py reverted clean; selector green again")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
