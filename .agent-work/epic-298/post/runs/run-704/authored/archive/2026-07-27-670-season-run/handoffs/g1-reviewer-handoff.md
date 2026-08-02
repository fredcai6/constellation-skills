# Reviewer Handoff

## Gate
`g1` — season runner + E-budget/refutil plumbing (#670 season-scale run)

## Survey State Location
Create your review survey at `.agent-work/670-season-run/g1-review/review.json`.

## What Was Implemented
(1) `src/physics/pilot/pipeline.py`: `run_circuit` gained keyword-only `budget_s` (default `E_WALLTIME_BUDGET_S`=180) and `refutil_db` (default `None` → the existing per-circuit scratch path), both forwarded to `run_stage_e` (previously `budget_s` was silently dropped). (2) NEW `scripts/run_season_670.py` — offline season runner (22-round 2023-Q slate, per-round DB grid read, scratch-copy-once, shared-refutil accumulation, detective vocabulary guard, park-on-missing). (3) NEW `scripts/verify_season_artifacts_670.py` — G2 acceptance check. (4) NEW `tests/unit/physics/pilot/test_season_runner.py` — 15 tests. Implementer result: `.agent-work/670-season-run/crew-results/g1-implementer-result.md`.

## How to Inspect the Diff
Review the UNCOMMITTED WORKING TREE in this worktree (C:/Programs/f1brainz-wt/epic659-670), NOT `git diff main...HEAD`. Use `git status --porcelain` then `git diff src/physics/pilot/pipeline.py` (tracked edit) and read the three new untracked files directly (`scripts/run_season_670.py`, `scripts/verify_season_artifacts_670.py`, `tests/unit/physics/pilot/test_season_runner.py`).

## Task Statement
Build the offline season runner as a PURE CONSUMER of the landed pilot machine, threading E-budget + shared-refutil as run-params, proven via unit tests only (no real E). Full task: `.agent-work/670-season-run/handoffs/g1-implementer-handoff.md`.

## Close Criteria (each becomes a review check)
- `run_circuit`→`run_stage_e` forwards `budget_s` AND `refutil_db` correctly; ALL defaults unchanged; run_circuit previously dropped budget_s — confirm it no longer does.
- `run_season_670.py` is a pure consumer: mints NO constant, edits NO frozen set, changes NO stage/gating logic, builds NO new model.
- OFFLINE: no fastf1 import / network call anywhere in the new code.
- NEVER writes a tracked `data/f1_data_*.db` — only the scratch copy is opened for write (verify the `test_tracked_db_never_written...` test actually guards this, and reason about the code paths — `shutil.copy` source read is fine).
- Per-round grid read from the DB (`session_classifications`, Q); park-on-missing is honest (recorded, no FastF1 pull).
- SHARED-refutil-DB accumulation is correct — rows from ≥2 rounds coexist with no silent drop/dup — and there is NO hand-rolled merge.
- VOCABULARY GUARD actually flags a divergent severity taxonomy (not vacuous). NOTE: it is DETECTIVE (flags after run_circuit returns) not preventive — this is scope-licensed (can't split E out of run_circuit). Confirm the flag is REAL and surfaces in `season_results.json` (`vocabulary_divergent`/`flagged_rounds`), and note in your findings that G2/G3 must surface flagged rounds. This detective-not-preventive limitation is ACCEPTABLE, not a BLOCK, given the scope exclusion — but confirm it's genuinely recorded, not silently pooled-and-hidden.
- `verify_season_artifacts_670.py` can actually FAIL (test the negative path — it must exit non-zero on missing/empty/no-fresh-round).
- New tests are REAL (assert observable behavior), not vacuous, and do NOT invoke real E.

## Allowed Scope
`src/physics/pilot/pipeline.py` (plumbing only); NEW `scripts/run_season_670.py`, `scripts/verify_season_artifacts_670.py`, `tests/unit/physics/pilot/test_season_runner.py`.

## Specific Exclusions (flag if touched)
No frozen-constant edit; no stage/gating logic change; no real compute run; no `docs/architecture/*` edit.

## Constraints the Implementation Must Respect
- OFFLINE only; never write tracked DBs; frozen consumed not minted; budget/refutil are run-params; Student-t σ preserved (not broken); pyright-0 on new code; pinned 3.14 interpreter.

## Map Anchors (inbound)
- **Structural:** `run_circuit`/`run_stage_e` (pipeline.py); `build_class_utilization_observables.py` (E CLI, INSERT OR REPLACE accumulates).
- **Constraints/assumptions:** offline-only; no-tracked-db-write; frozen-consumed-not-minted; budget-is-run-param.
- **Decision anchors:** decision:consolidated-slice — shared-DB accumulation, no merge. `@grade: settled/measured · leans g1-implement,g3,g4`
- **Evidence expectations:** plumbing forwards correctly; shared-DB accumulates no-dup; vocabulary-guard flags; tracked-DB never written.
- **Map confidence flags:** epic-659 map deferred to #671 → verify vs source, not a packet.

## Evidence Produced
- `pytest tests/unit/physics/pilot/test_season_runner.py -q` → `15 passed`; `pytest tests/unit/physics/pilot -q` → `44 passed` (29 existing + 15 new); pyright → `0 errors`. Re-run these yourself to confirm; the target integrate postcondition is `g1-integrate.c1` (the test command).

## Suggested Model Tier
`stronger` — reason: load-bearing offline/reversibility contract; the plumbing crosses a subprocess boundary and the shared-DB accumulation correctness is subtle.

## Stop Conditions
BLOCK if: the diff cannot be accessed, evidence is absent/unverifiable, the runner writes a tracked DB, a frozen set was edited, stage/gating logic changed, or the vocabulary divergence is silently pooled-and-hidden (vs honestly flagged).

## Return Format
Write REVIEW_RESULT to `.agent-work/670-season-run/crew-results/g1-reviewer-result.md` (verdict APPROVE or BLOCK, per-check findings, blockers, out-of-scope observations, workflow feedback). Then SendMessage cmdr-670 a thin pointer (verdict + result path) before ending your turn.
