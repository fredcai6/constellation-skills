# Reviewer Handoff

## Gate
`g1-review`

## Survey State Location
Create your review survey checklist at `.agent-work/egaw-red-without-git/g1-review/review.json`.

## What Was Implemented
`tests/test_episode_observation_guard_at_write.py`'s `RedBeforeGreenAfterTests.
test_bare_verb_workaround_was_accepted_before_this_change` used to reconstruct a pre-change revision of
`scripts/apply_episode_delta.py` via `git show 2c46cab8:...` — broken on CI's shallow clone and dependent
on a hardcoded commit SHA. It was rewritten to instead take the CURRENT writer (`load_current()`),
monkeypatch its `_reject_instruction_shaped` function to a no-op, run the identical delta through it and
assert it writes cleanly, then restore the original function in a `finally` block and move on (the
existing `test_bare_verb_workaround_is_rejected_now` then shows the identical delta rejected with the
guard restored). The now-dead git machinery (`PRE_CHANGE_REV`, `_git_show`, `load_pre_change`) and the
now-unused `import subprocess` were deleted; the module docstring and the rewritten test's own docstring
were updated to describe the new mechanism.

## How to Inspect the Diff
Uncommitted working tree in `/home/tommy/projects/constellation-skills/.worktrees/episode-guard-at-write`.
Run `git status --porcelain` then `git diff -- tests/test_episode_observation_guard_at_write.py`.

## Task Statement
Per LAUNCH_ORDER.md ("egaw-red-without-git"): remove the test's git dependency without losing what the
RED/GREEN pair proves — that the write-time guard PR #592 added is what causes the rejection, not merely
present. LAUNCH_ORDER.md names two options and leans toward (a) exercise the current writer with the
guard call neutralized; that is the option implemented here.

## Close Criteria
- The rewritten test still proves attribution: with the guard neutralized the delta writes cleanly; with
  it restored (the existing, unmodified `test_bare_verb_workaround_is_rejected_now`) the identical delta
  is rejected. Both against `load_current()` — no historical/resurrected module involved.
- No `git`, `subprocess`, or the literal SHA `2c46cab8` anywhere in the file.
- `python -m pytest -q tests/test_episode_observation_guard_at_write.py` — all tests pass, none skipped.
- No `pytest.skip` added anywhere in the file.
- Only `tests/test_episode_observation_guard_at_write.py` is changed in the source tree (work-area
  artifacts under `.agent-work/` don't count against this).
- The monkeypatch restores the original function even if the delta run raises (i.e., it's in a `finally`,
  not bare sequential code) — otherwise a failure mid-test would leak a neutralized guard into whichever
  test runs next in the same process.

## Allowed Scope
`tests/test_episode_observation_guard_at_write.py` only (implementer was also allowed to READ, never
modify, `scripts/apply_episode_delta.py`).

## Specific Exclusions
Everything in LAUNCH_ORDER.md's "File Ownership — NOT yours" list — flag as a BLOCK if any of them show
as changed: `.github/workflows/ci.yml`, `scripts/apply_episode_delta.py`,
`scripts/verify_episode_observations.py`, `tests/test_episode_observations.py`,
`scripts/install_constellation.py`, `scripts/hooks/spine_rail.py`, `.claude/settings.json`, `.mcp.json`,
existing `episodes/` records.

## Constraints the Implementation Must Respect
- Do not delete the RED test or reduce it to a no-op.
- No hardcoded commit SHA anywhere in the file after this change.

## Map Anchors (inbound)
- **Structural:** `scripts/apply_episode_delta.py:996-1010` (`_reject_instruction_shaped`, the seam being
  neutralized/restored), `tests/test_episode_observation_guard_at_write.py:117-149`
  (`RedBeforeGreenAfterTests`, where the change lands).
- **Decision anchor:** approach (a) is ratified in LAUNCH_ORDER.md — not the reviewer's to relitigate;
  flag only if the IMPLEMENTATION deviates from it, not if the choice itself seems debatable.
- **Evidence expectations:** claim:attribution (rejection caused by the guard call, not merely present),
  claim:no-git (grep for git/subprocess/2c46cab8 returns nothing).

## Evidence Produced
From IMPLEMENTER_RESULT (`.agent-work/egaw-red-without-git/crew-handoffs/g1-implement-implementer-result.md`):
- `pytest -q tests/test_episode_observation_guard_at_write.py` → 9 passed.
- `grep -n "2c46cab8\|import subprocess\|git show\|_git_show\|load_pre_change\|PRE_CHANGE_REV" tests/test_episode_observation_guard_at_write.py` → no output.
- `git diff` scoped to the one file.
The dispatching Commander independently reproduced both commands with the same results before this
review was dispatched — re-verify them yourself rather than trusting that claim.

## Suggested Model Tier
simple bounded — one file, one rewritten test method, mechanical verification.

## Stop Conditions
Return BLOCK if: the diff touches anything outside the allowed scope, the rewritten test does not
actually prove attribution (e.g. it would pass even if the guard call were deleted entirely, not just
neutralized), any git/subprocess/SHA reference remains, or a `pytest.skip` was added.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings, blockers, out-of-scope
observations, workflow feedback.

Write the full `REVIEW_RESULT` to `.agent-work/egaw-red-without-git/crew-handoffs/g1-review-reviewer-result.md`
before you finish.
