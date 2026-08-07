# Reviewer Handoff

## Gate
g2 (issue #328, workstream D of epic #418)

## Survey State Location
Create your review survey checklist at
`.agent-work/issue-422-wire-invariants/g2-review/review.json`.

## What Was Implemented
`scripts/checklist_engine.py`'s `record()` (the survey verb) now evaluates `command`-kind postconditions
when `result == 'pass'` is requested — mirroring `advance()`'s existing pattern via the same
`_check_condition` helper and the same `EngineError` refusal shape; `result == 'fail'` is never gated.
`INTERROGATION.template.json`'s `zc-consolidate` and `REVIEW_SURVEY.template.json`'s `r6-fowler` each now
carry a real command postcondition wired to `verify_interrogation.py`/`verify_fowler_pass.py`, using a
hand-fill placeholder convention (documented in each item's imperative text). `tests/test_record_postcondition_wiring.py`
lands 10 tests, including real unmocked deliberate-breakage tests against the actual verify scripts.

## How to Inspect the Diff
Uncommitted working tree in this worktree (`C:/Programs/constellation-skills-wt/epic418-d-422`):
`git status --porcelain`, then `git diff -- scripts/checklist_engine.py
skills/interrogator/templates/INTERROGATION.template.json
skills/reviewer/templates/REVIEW_SURVEY.template.json`, and read the new file
`tests/test_record_postcondition_wiring.py` directly. NOTE: a sibling gate (g1, issue #329) already landed
and is committed on this branch — its files (`scripts/verify_worktree_precondition_coverage.py`,
`tests/test_worktree_precondition_wiring.py`, a prior change to `COMMANDER_SPINE.template.json`) are NOT
part of this review; ignore them.

## Task Statement
Rewire two invariants currently backed by a `record()`-survey (stores whatever the agent types, invokes
nothing) into real command checks: extend the engine's `record()` verb to actually evaluate command
postconditions, then wire `zc-consolidate`/`r6-fowler` to the existing `verify_interrogation.py`/
`verify_fowler_pass.py` scripts. Prove it with deliberate-breakage tests landed in the automated suite.

## Close Criteria
- `record()` refuses `result='pass'` when a `command`-kind postcondition fails; does not block
  `result='fail'`; items with NO command postcondition are byte-for-byte unaffected — this is the
  regression floor, confirm `tests/test_checklist_engine.py` is unchanged in behavior and still green.
- `zc-consolidate`/`r6-fowler` each carry exactly one new command postcondition; both templates remain
  valid JSON; no other item in either template touched.
- `tests/test_record_postcondition_wiring.py` passes AND you independently re-prove the deliberate-breakage
  claim yourself — do not trust the report. The implementer's reported method: `git stash push --
  scripts/checklist_engine.py`, re-run the new test file (expect exactly the 3 refusal-dependent tests to
  fail with `AssertionError: EngineError not raised`, 7 others still pass), `git stash pop`, re-run (expect
  10 passed). Reproduce this exactly and confirm the failure count/shape matches.
- **Fence check (critical for this gate)**: diff the FULL `checklist_engine.py` file, not just the reported
  hunk — confirm `render_human`, `_why_suffix`, and `current()` are byte-identical to before (workstream
  B/#420 owns that path this wave; a collision here is a BLOCK, not a note).
- Full suite green: `python -m pytest tests/ -q` (use `python`, not `py`, if `py` lacks pytest in your
  environment — verify with `python -m pytest --version` first).

## Allowed Scope
`scripts/checklist_engine.py` (invariant-check path: `record`, `main()`'s CLI dispatch for `record` only),
`skills/interrogator/templates/INTERROGATION.template.json` (`zc-consolidate` only),
`skills/reviewer/templates/REVIEW_SURVEY.template.json` (`r6-fowler` only), new file
`tests/test_record_postcondition_wiring.py`.

## Specific Exclusions
`scripts/verify_interrogation.py`, `scripts/verify_fowler_pass.py` (must be byte-identical — confirm with
`git diff` showing nothing for both), `checklist_engine.py`'s rendering path (`render_human`,
`_why_suffix`, `current()`), any other item in either template, issue #315 (not required to be fixed here).

## Constraints the Implementation Must Respect
- Reuses `_check_condition` (no reimplementation of condition-checking logic).
- `null`/`artifact`-kind postconditions on survey items remain unevaluated by `record()` — confirm a
  comment exists at the code site naming this limit explicitly, per Tommy's scope ruling (this is a
  documented, sanctioned narrowing, not a gap to flag as a defect).
- The deliberate-breakage fixtures must invoke the REAL, unmodified verify scripts against real bad files
  in `tmp_path` — not mocked/stubbed commands. Confirm by reading the test file directly.

## Map Anchors (inbound)
Inherited from g2-implement (same as the mission frame's g2 anchors):
- **Structural:** `scripts/checklist_engine.py:1731` `record()`; `:1668` `advance()`; `:1699` the
  postcondition-check line mirrored.
- **Capability:** Survey `record()` verb — now provably checks a `pass` result on a command-backed item.
- **Constraints/assumptions:** all 7 pre-existing `kind: command` postcondition examples in the corpus
  live on GATED spines only.
- **Decision anchors:** `decision:survey-record-check-scope` — command-kind postconditions only, by
  Tommy's scope ruling. `@grade: settled/human · leans g2-implement` — this is NOT yours to revise; if you
  believe artifact/null-kind coverage is actually needed, flag it as a decision candidate, don't build it.
- **Evidence expectations:** `claim:record-ignores-postconditions` — the red-before/green-after
  demonstration IS the required re-confirmation.

## Evidence Produced
See `.agent-work/issue-422-wire-invariants/crew-handoffs/g2-implement-result.md` for the implementer's full
pasted command output (json validation, targeted + regression + full-suite runs, the git-stash red/green
demonstration, wiring grep). Target postcondition this evidence backs: `g2-integrate.c1` (full-suite test
command) and `g2-integrate.c2` (this review's verdict).

## Suggested Model Tier
Sonnet — bounded verification of a precedented engine extension with an explicit fence to check.

## Stop Conditions
Stop and return BLOCK if: the rendering-path fence was violated (any diff in `render_human`/`_why_suffix`/
`current()`); the deliberate-breakage tests do not actually fail when you independently strip the fix;
`verify_interrogation.py`/`verify_fowler_pass.py` show any diff; the full suite is not green; a survey
item's existing (non-command-postcondition) `record()` behavior changed.

## Return Format
Return REVIEW_RESULT (verdict APPROVE/BLOCK, per-check findings, blockers, out-of-scope observations,
workflow feedback). Report it as your final message text; also write it to
`.agent-work/issue-422-wire-invariants/crew-handoffs/g2-review-result.md`.
