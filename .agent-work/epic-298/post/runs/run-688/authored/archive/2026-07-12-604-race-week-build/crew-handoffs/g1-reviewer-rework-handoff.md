# Reviewer Handoff — REWORK re-review (attempt 2)

## Gate
`g1-review` (re-run after g1-implement rework)

## Survey State Location
`.agent-work/604-race-week-build/g1-review-r2/review.json`

## What Was Implemented
Rework fix for the BLOCKING finding from the first review pass (see
`.agent-work/604-race-week-build/crew-handoffs/g1-review-result.md` Blockers section): `explain_stage`
in `scripts/race_week_stages.py` could raise on a malformed `explainer_path` (`None`/`""`),
contradicting its documented "never raises" contract. Fix: moved `Path(explainer_path)`/
`with_name(...)` construction inside the `try:` block; added a fixed tempdir fallback stub path for
when `explainer_path` itself can't be constructed; added 2 regression tests. Full fix + evidence at
`.agent-work/604-race-week-build/crew-handoffs/g1-implementer-result-r2.md`.

## How to Inspect the Diff
Worktree `C:/Programs/f1Brainz/.claude/worktrees/604-build`, branch `feat/604-race-week-build`. Read
`scripts/race_week_stages.py`'s `explain_stage` function directly (it's short) and diff it mentally
against the version quoted in the original BLOCK finding. Everything else in the file (checkpoint
I/O, `discover_sessions_stage`, `predict_stage`, `optimize_stage`) was already reviewed clean in the
first pass and should NOT have changed — spot-check that it hasn't (e.g. `git diff` against the
attempt-1 state is not directly available since nothing was committed yet, but the handoff scoped
the rework to `explain_stage` + new tests only — confirm no other function's body changed).

## Task Statement
Confirm the specific bug is actually fixed (re-derive the fix's correctness yourself, don't just
trust the pasted before/after), confirm nothing else regressed, and confirm the new regression tests
actually exercise the failure mode (not just superficially named).

## Close Criteria
- `explain_stage(<valid stem>, None)` and `explain_stage(<valid stem>, "")` both return cleanly
  (a dict with a `status` field) — reproduce this yourself, live, in the worktree; do not trust the
  implementer's pasted transcript alone.
- The fallback stub path (when `explainer_path` itself can't be constructed) is itself guaranteed
  constructible and is not silently writing into the repo/cwd in a surprising way — check where
  `tempfile.gettempdir()` actually resolves to and whether that's a reasonable choice (note it, it
  doesn't have to be perfect, just not silently broken).
- No other function in `scripts/race_week_stages.py` changed from the version already
  APPROVED-equivalent in the first review pass.
- Full test suite (`tests/unit/scripts/test_race_week_stages.py`) passes — re-run it yourself.
- `py -m src.utils.simplification_limits --paths scripts/race_week_stages.py` passes.

## Allowed Scope
Same as original: `scripts/race_week_stages.py` + `tests/unit/scripts/test_race_week_stages.py` only,
this pass scoped specifically to the `explain_stage` fix + 2 new tests.

## Specific Exclusions
No other function should have changed. No `scripts/race_week.py`. No `src/` changes.

## Constraints the Implementation Must Respect
Same as the original g1-review handoff (unaffected by this fix) — re-verify db-path/compound-prior
threading and the no-double-write constraint are still intact (they should be untouched, confirm).

## Map Anchors (inbound)
Same as `g1-implement`'s anchors in `execute.json` (unchanged by this rework).

## Evidence Produced
IMPLEMENTER_RESULT (rework) at
`.agent-work/604-race-week-build/crew-handoffs/g1-implementer-result-r2.md`: 33/33 tests pass (31
original + 2 new), full pytest output pasted, before/after repro of the fix, simplification_limits
PASS. Target postcondition: `g1-integrate.c1`/`g1-integrate.c2`.

## Suggested Model Tier
Sonnet — narrow, well-scoped re-review of a targeted bug fix.

## Stop Conditions
Return BLOCK if the fix doesn't actually hold up under your own live reproduction, if any other
function changed unexpectedly, or if the new tests don't actually exercise the failure mode.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings, blockers, out-of-scope
observations, workflow feedback.
