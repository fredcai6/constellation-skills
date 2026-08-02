# Implementer Handoff — G1 (Issue #383)

## Task
Populate per-event `entity_count` at the gold-cycle backtest producer so the calibration `β·effective_dof`
term engages, add a regression test, and demonstrate dof engagement.

## Protected intent
- One canonical path: fix at the single producer (`evaluate_labeled_batches`), not each consumer.
- Do NOT change committed `aggregate_metrics` / `backtest_metrics` shape.
- `entity_count` is already declared in `gold_report_schema.py` — no schema shape change.

## Changes
1. `src/evo_predictor/module_training_orchestration.py`, `evaluate_labeled_batches` (~L624): add
   `"entity_count": len(batch.entity_ids)` to the per-event **row top-level** (the dict that already has
   `event_id`, `entity_ids`, `metrics`). MUST be row-level, NOT inside `metrics` (because `_mean_metrics`
   at L646 averages every metrics key and would create a spurious `aggregate_metrics.entity_count` and
   change committed shape).

2. Regression test in `tests/unit/evo_predictor/test_evaluate_labeled_batches.py`:
   - `per_event[0]["entity_count"]` is a positive int equal to `len(entity_ids)` (== 3 for the fixture).
   - `entity_count` is NOT present in `metrics` nor in `aggregate_metrics` (no pollution).

3. Flow-through test in `tests/unit/evo_predictor/test_gold_module_cycle.py`:
   - `event_metric_rows` carries `entity_count` from the row top-level into the emitted row.

4. Dof-engagement demonstration test in `tests/unit/evo_predictor/test_gold_cycle_runner.py` (calibration
   home): with realistic VARYING per-event entity counts, the calibration's `β·effective_dof` term is
   non-constant across events (the `_effective_dof` values differ; a fitted β makes the calibrated trace
   vary by field size), AND with `entity_count=None` (the bug) the dof collapses to constant 1. This
   guards against regression to the inert constant-dof state.

## Definition
`entity_count = len(batch.entity_ids)` — scored field size. `PairBatch.__post_init__` enforces
`len(entity_ids) >= 2`, so every scored event yields a positive int. Matches existing
`module_runtime.py:115` definition.

## Test mode
Test-led. Run targeted subsets only:
`py -m pytest tests/unit/evo_predictor/test_evaluate_labeled_batches.py tests/unit/evo_predictor/test_gold_module_cycle.py tests/unit/evo_predictor/test_gold_cycle_runner.py tests/unit/evo_predictor/test_gold_cycle_task_calibration.py -q`
Then `py -m src.utils.simplification_limits` on touched paths; pyright on touched files if available.

## Exclusions
- Do NOT fix `pair_count` (separate triage candidate, same root cause).
- Do NOT touch `module_uncertainty_diagnostics` `_SIGMA_ERROR_CORR_KEYS` (sibling #384).
- Do NOT regenerate the whole schema doc; field already declared.

## Authority
Proceed under Admiral standing orders. Cheap/reversible decisions already logged in problem_statement.md.
