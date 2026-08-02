# Triage Recommendation: `pair_count is None in gold-cycle event_level_metrics (same root cause as #383)`

## Classification
`bug`

## Source checklist/artifact
- review finding (g1-review, #383 run); `.agent-work/issue-383-entity-count/execute.json` triage_candidates tc1

## Structural anchor
`struct:evo.gold_cycle` / src/evo_predictor/module_training_orchestration.py

## Cartographer mismatch class
`none`

## Problem
Every `modules[].event_level_metrics[].pair_count` in the gold-cycle details.json is `None`, exactly
like `entity_count` was before #383. The producer `evaluate_labeled_batches` never emits `pair_count`
on its per-event rows; downstream `event_metric_rows` reads `event.get("pair_count") or
metrics.get("pair_count")`, both absent -> None.

## Current truth
- `evaluate_labeled_batches` (module_training_orchestration.py ~L624) builds per-event rows with
  `event_id`, `entity_ids`, `entity_count` (now), and `metrics` — but no `pair_count`.
- `batch.pair_index.shape[0]` is the pair count and is available at that site.
- Confirmed in committed reports/evo/gold_cycle_260603_173742_2018thru2024.details.json: all 288 scored
  events have pair_count = None.

## Desired/future concern
Populate `pair_count` at the same producer, the same way entity_count was fixed in #383
(row top-level, not in metrics). Unlike entity_count, pair_count has no current consumer that is
silently disabled — so this is lower urgency (diagnostic completeness, not a disabled mechanism).

## Evidence
- src/evo_predictor/gold_module_cycle.py L112: `row["pair_count"] = event.get("pair_count") or metrics.get("pair_count")`
- committed details.json: 288/288 scored events pair_count=None
- #383 fix pattern (commit 85f4a7d) is directly reusable

## Impact
Diagnostic field declared in the schema but never populated; weakens per-event traceability. No known
disabled mechanism depends on it (contrast entity_count -> calibration dof), so correctness impact is low.

## Suggested scope
- Add `"pair_count": int(batch.pair_index.shape[0])` to the per-event row in `evaluate_labeled_batches`.
- Regression test asserting pair_count is a positive int per scored event.

## Non-goals
- Do not change aggregate_metrics shape (keep pair_count at row level, not in metrics).
- No schema shape change (pair_count already declared).

## Acceptance criteria
- [ ] pair_count is a positive int per scored event in details.json
- [ ] regression test guards it

## Recommended priority
`low`

**Reason:** Cosmetic/diagnostic completeness; no disabled mechanism depends on it. Trivial one-line fix
plus a test, mirrors #383 exactly.

## Related artifacts
- #383 (this run), commit 85f4a7d
- src/evo_predictor/module_training_orchestration.py

## Issue creation authority
`ask user`
