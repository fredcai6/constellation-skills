# Problem Statement — Issue #383

## Bug
Every `modules[].event_level_metrics[].entity_count` in the gold-cycle `details.json` is `None`.
Confirmed empirically: in committed `reports/evo/gold_cycle_260603_173742_2018thru2024.details.json`,
**288/288 scored events across all 12 modules have `entity_count = None`** (and `pair_count` too).

## Root cause (single site)
`evaluate_labeled_batches` in `src/evo_predictor/module_training_orchestration.py` (~L611-628) is the
backtest scorer that produces the `per_event` records consumed by the gold reporter. It builds each
per-event `metrics` dict (field_std, sigma_pi_trace, NLL, rank metrics) and a row carrying
`entity_ids`, but it **never emits `entity_count`**. Downstream:
- `event_metric_rows` (`gold_module_cycle.py` L111): `row["entity_count"] = event.get("entity_count") or metrics.get("entity_count")` -> both absent -> None.
- `_parse_loso_event_rows` (`runner_support.py` L864): same read -> None.
- Both calibration paths (`gold_cycle/calibration.py`, `gold_cycle/task_calibration.py`): `_effective_dof(None)` -> returns constant 1, so the `beta * effective_dof` term is a constant offset; the dof *scaling* the formula intends never engages.

## Definition (canonical)
`entity_count = len(batch.entity_ids)` — the scored field size for the event.
- Already used identically in `module_runtime.py` L115 (`"entity_count": len(batch.entity_ids)` in field-result diagnostics).
- `PairBatch.__post_init__` (`src/latent_power/models.py` L54-55) enforces `len(entity_ids) >= 2`,
  so every scored event provably has a positive int (>= 2) entity_count.

## Fix
Populate `entity_count = len(batch.entity_ids)` at the producer `evaluate_labeled_batches`, on the
per-event **row top-level** (next to `entity_ids`), NOT inside the `metrics` dict. Rationale:
`_mean_metrics` (L646) averages every key in `metrics`; adding entity_count there would create a
spurious `aggregate_metrics.entity_count` and change the committed aggregate shape. Row-level placement
flows to all three consumers (each reads `event.get("entity_count")` first) with zero side effects.

## Protected intent / invariants
- One canonical path: fix at the single producer; do not patch each consumer.
- Do not change committed `aggregate_metrics` / `backtest_metrics` shape.
- `entity_count` field is already declared in `gold_report_schema.py` (L246) and the generated schema
  doc; we populate an already-declared field — no schema *shape* change.

## Acceptance (from issue + Admiral standing orders)
1. `entity_count` is a positive int per scored event in details.json.
2. The calibration's `beta * effective_dof` term is CONFIRMED to engage (non-constant across events) —
   unit-level demonstration on the calibration path with realistic per-event entity counts is acceptable
   (Admiral standing order; avoids slow full gold cycle).
3. Regression test guarding it.

## Scope boundary
- IN: producer emission of entity_count; regression test; dof-engagement demonstration.
- OUT (sibling #384): `module_uncertainty_diagnostics` `_SIGMA_ERROR_CORR_KEYS` key-set reconciliation.
- DISCOVERED (triage candidate, not in scope): `pair_count` is None everywhere via the same root cause
  (adjacent missing field). Note for the Admiral; do not fix here unless trivially free.

## Decisions taken (Admiral async — defensible defaults, cheap/reversible)
- D1: Fix at producer (q2). D2: entity_count = len(batch.entity_ids) (q3). D3: positive int on scored
  events only; skipped events legitimately None (q4). D4: row-level placement, not metrics (q8).
  D5: unit-level dof demonstration over full gold cycle (q5). D6: no schema-shape change / no generated
  doc rewrite (q6).
