# Review Result

## Assigned Gate
`g5` re-review (issue #456), attempt 2 — remediation of attempt-1's `BLOCK` on `SPLIT_LEGEND`

## Result
`APPROVE`

## Handoff compliance
Yes. Commit `588d5419` does exactly what the Commander's ruling asked: reword `SPLIT_LEGEND` in
both hand-independent copies (`render.py:361`, `checks.py:301`) to state the rule `is_test_module`
actually applies, add a pinning test (`test_the_legend_states_the_rule_the_predicate_actually_
applies`), and fix `measure_split.py`'s headline to carry the definer dimension (the predicate
itself untouched in both files, confirmed by diff). All four "where to spend your budget" attack
targets from the handoff were attacked, not merely reproduced — full detail below and in the
survey (`.agent-work/issue-456/g5-rereview/review.json`).

## Scope drift
None. `git diff --name-only 1f5c8a6e..588d5419 -- scripts/ tests/` is exactly the three files the
handoff names, plus `measure_split.py` (explicitly in scope). Every DO-NOT-TOUCH anchor
(`_make_collision_repo`, `OWN_MODULE_NAMED_MUTATION`, `LEGEND_DROPPED_MUTATION`,
`entity_symbol_join`, `page_location_matches_content`, page-header line positions, the non-ASCII
pages) re-verified untouched by grep and by a fresh 3865-page scan, not by reading the RESULT's
claim. `map/` still has 0 tracked files; no `git add -A` residue.

## Evidence verdict
Satisfies required evidence, independently reproduced this run: fresh build 111/3753/3865, fresh
check 7/7, gate selector (tc38, run by hand with `FORCE_COLOR`/`PYTHONIOENCODING` cleared) 20
passed, full suite (backgrounded to completion per the handoff, never polled as a buffered file)
1781 passed / 2 skipped / 672 subtests / 0 failed — exact matches, baseline+1 throughout.
`measure_split.py` reran to 88/2341/2/449/873/0, byte-for-byte match, cross-checked against a
second independently-written measurement script with identical results.

The one honest gap, not smoothed over: the pinning test's wording half
(`assertNotIn("top-level", legend)`) is a pin against one literal string, not a semantic pin
against the overclaim class — proved by mutating the legend to four differently-worded
top-level-only overclaims that all survive undetected. This does not fail the item: the test's own
docstring is honestly scoped to guarding a reversion of that specific wording, and its behavioural
half (a nested tests package still classifies correctly in both copies) is a full, unaffected pin
on the actual code path. Filed as a triage candidate, not required-evidence failure.

## Code/doc quality
Fowler pass: 12/12 baseline smells rendered a verdict, rail exit 0 (`.agent-work/issue-456/
g5-rereview/fowler-pass.json`). Zero flagged, one overridden with a logged and re-earned reason
(duplicated-code on the two `SPLIT_LEGEND` copies — this run's own independence attack proves the
override is earned: diverging only `checks.py`'s copy still makes two independent checks go red).
The legend is now literally TRUE of `is_test_module`'s real code in both files, both halves
(filename convention and package-anywhere-on-path), read side by side.

## Map impact verdict
- **Evidence supports claimed change:** Yes — the reworded legend is verified true of the
  predicate; the corrected `measure_split.py` headline is reproduced independently.
- **Constraints not violated:** Yes — `is_test_module`'s predicate untouched, zero entities
  reclassified (verified by diffing the exact pre/post page-filename sets across a throwaway
  worktree build at the pre-remediation commit, not by cell-count matching alone).
- **Notes match the diff:** Yes — the RESULT's "behavior changed" section (page text only, not
  classification) matches exactly what the diff shows.
- **Decision candidates surfaced:** N/A — no new authority-requiring decision in this remediation;
  the Commander's ruling was already the decision.
- **Durable context routed:** Yes — one new triage candidate filed this run (the narrow wording
  pin); two of attempt-1's own triage candidates (legend-pinning check, `measure_split.py` definer
  fix) are now fulfilled and should be marked closed against `588d5419`.

## Reconciliation check
No architecture-level divergence. This is exactly the narrow fix the ruling called for — no design
change, no new structural surface. See `r5-reconciliation` in the survey for the full triage
reconciliation.

## Blockers
- none

## Out-of-scope observations
- tc1 (filed via the engine, `r7-pin-attack`): the new pinning test's wording half is a pin
  against the one literal string "top-level," not a semantic pin against the overclaim class.
  Mutation-proved: four differently-worded top-level-only overclaims that avoid that literal
  substring all survive undetected. Not a blocker — the test's docstring does not overclaim its
  own coverage, and the behavioural half is a full, general pin. Worth strengthening later, e.g.
  deriving `SPLIT_LEGEND`'s prose from the predicate's own literal values.
- Two of attempt-1's own triage candidates (g5-review tc1: legend-pinning check; tc2:
  `measure_split.py` definer-blind headline) are now fulfilled by this remediation and should be
  marked closed against commit `588d5419` rather than left open as still-pending asks.

## Workflow Feedback

- **Handoff gaps:** none — the handoff was complete, specific, and its four "where to spend your
  budget" attack targets were exactly the right places to spend budget; each surfaced something
  (three confirmed solid, one real-but-honestly-scoped narrowness).
- **Context rediscovered:** none beyond what the handoff and prior gate artifacts (attempt-1's
  `g5-review/review.json`, `g0-rereview/review.json` as a structural precedent for a re-review
  survey) already carried.
- **Instructions improvised around:** the survey template's `r6-fowler` postcondition command
  worked cleanly this run because I resolved `<fowler-pass-record-path>` to the real path at
  instantiation time (before `claim`), per the item's own "NORMAL PATH" guidance — no waiver
  needed, unlike `g0-rereview`'s waiver-forced path when that substitution was skipped. Worth
  reinforcing in the template's imperative text as the default expectation, since at least one
  prior re-review needed a forced waiver for the same postcondition.
- **What would have made this easier:** nothing structural. One small friction: the Bash tool in
  this worktree refuses `cd <dir> && <cmd> > file` as "too complex to verify it stays inside the
  worktree" even when the cwd is already that worktree — dropping the redundant `cd` prefix
  resolved it immediately. Worth noting in the shell-quoting guidance for the next crew.

## Return status
`complete`
