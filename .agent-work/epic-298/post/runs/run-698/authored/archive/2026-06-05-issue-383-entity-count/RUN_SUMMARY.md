# Run Summary — Issue #383 (Commander)

## Outcome: COMPLETE. PR #401 opened against main (NOT merged — Admiral merges).

## What shipped
- `src/evo_predictor/module_training_orchestration.py` `evaluate_labeled_batches`: per-event row now
  carries `entity_count = len(batch.entity_ids)` (row top-level, not in `metrics`).
- 6 regression/demonstration tests across `test_evaluate_labeled_batches.py`,
  `test_gold_module_cycle.py`, `test_gold_cycle_runner.py`.
- Commit: 85f4a7d on branch `constellation/issue-383-entity-count` (base fa9e48b = origin/main).

## Root cause (one site)
The backtest scorer that produces per-event rows never emitted `entity_count`; downstream
`event_metric_rows`/`_parse_loso_event_rows`/calibration all read `event.get("entity_count") or
metrics.get("entity_count")` → None → `_effective_dof(None) → 1` → the `β·effective_dof` calibration
term was a constant offset (dof scaling inert). Confirmed empirically: 288/288 scored events None in
committed details.json.

## Acceptance — all met
1. entity_count positive int per scored event — emitted as len(batch.entity_ids); PairBatch enforces
   ≥2; tested + red-checked (KeyError without fix).
2. dof term engages (non-constant) — unit-level demo: effective_dof [17,19,21,14] vs bug [1,1,1,1];
   objective optimum at β=0.1 with populated counts, inert with None. Evidence:
   evidence/dof_engagement_demo.txt.
3. regression test guarding it — 6 tests.

## Verification
- py -m pytest targeted: 106 passed (scorer/reporter/calibration/schema). No full suite run.
- py -m pyright on touched src + tests: 0 errors, 0 warnings.
- py -m src.utils.simplification_limits --baseline: exits 0; evaluate_labeled_batches 0 violations.

## Spine ledger (all complete/skipped)
init✓ context✓ understand✓ plan✓ compact(skip: lean ctx)✓ execute✓ reconcile✓ triage✓ review✓ archive✓
Execute gate G1: implement✓ review(APPROVE)✓ integrate✓.

## Architecture
No map edit required — populated an existing field in the already-mapped
evaluate_labeled_batches → backtest JSON → event_metric_rows → calibration flow (struct:evo.gold_cycle).

## Decisions taken (Admiral async — defensible defaults)
- D1 fix at producer; D2 entity_count=len(entity_ids); D3 positive int on scored events only (skipped
  stay None); D4 row-level not metrics (avoid aggregate pollution); D5 unit-level dof demo over full
  gold cycle; D6 no schema-shape change / no generated-doc rewrite; D7 compact skipped (lean context).
- Triage filing DEFERRED to Admiral (low-priority follow-ups; not filing is reversible).

## Deferred / discovered (issue-ready, NOT filed — Admiral approval needed)
- tc1 pair_count None via same root cause (low). triage-candidates/tc1_pair_count.md
- tc2 committed details.json stale until next gold cycle (low). triage-candidates/tc2_stale_details.md

## Coordinates
- Branch: constellation/issue-383-entity-count
- PR: #401 (https://github.com/fredcai6/f1Brainz/pull/401)
- Worktree: C:/Programs/f1Brainz/.claude/worktrees/agent-a7bf91d5e32f2d829
