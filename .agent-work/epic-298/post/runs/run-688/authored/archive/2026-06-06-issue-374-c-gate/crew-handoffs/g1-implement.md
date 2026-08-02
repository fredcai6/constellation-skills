# Implementer Handoff — G1: meta-learner data-builder

## Gate
`g1`

## Task
Create `scripts/fusion_replay/metalearner.py` (NEW file) containing a **data-builder only** (no modelling) that produces, per task, a pooled **pairwise** supervised dataset from already-generated per-event module records. REUSE the existing fusion_replay harness — do NOT reimplement record loading, the canonical join, the constructor-lineage normalizer, or constructor→driver projection.

## Protected Intent
This feeds a Step-3 gate measuring interaction headroom over module outputs. The dataset must faithfully represent the four module pi values per entity exactly as the production scoring harness sees them (after the same alignment/lineage handling), so downstream Model1/Model2 numbers are comparable to issue #373's ceilings. ANY divergence from the harness's per-event preprocessing corrupts the gate.

## Test Mode
TDD required. Write the test FIRST: it must load REAL records and assert structure/invariants.

## THE REUSE RECIPE (follow this exactly — it is the whole point of the gate)
The Commander has traced the harness. Your data-builder must mirror `scorecard._run_task`'s prelude, then per-event mirror the `scorecard._compute_event_residuals` alignment idiom. Concretely, in `scripts/fusion_replay/metalearner.py`:

```python
from pathlib import Path
from scripts.fusion_replay.scorecard import (
    _module_meta_for_task, _load_module_events, canonicalize_and_join,
    _preprocess_events, _build_module_field_results, _align_driver_pi,
)
from src.evo_predictor.fusion_training._calibration import module_names_for_task
from src.evo_predictor.constructor_projection import project_constructor_field_to_drivers
from src.data.database import DatabaseManager  # only if you need db_cache typing; _preprocess_events builds its own
```

Per task:
1. `module_order = list(module_names_for_task(task))`  → canonical order is `[constructor_*_recent, driver_*_recent, constructor_*_weekend, driver_*_weekend]` (indices 0,1,2,3).
2. `module_meta = _module_meta_for_task(task)`
3. `loaded = {mn: _load_module_events(records_dir, mn) for mn in module_order}`
4. `joined, join_counts = canonicalize_and_join(loaded, task)`
5. `db_cache = {}` then `prepped, miss_counts = _preprocess_events(joined, module_meta, module_order, task, db_cache)`
   - Each element of `prepped` is a dict with: `canonical_key` (`"year:round:gp:task"`), `driver_ids` (tuple, ≥3, team-validated + lineage-remapped), `constructor_by_driver`, `event_arrays`, `actual_positions` (aligned to driver_ids), `target_mu`.
6. Per prepped event, get the aligned 4-column pi matrix `M` of shape `(n_drivers, 4)`. Build it EXACTLY like `_compute_event_residuals` does (do NOT hand-roll):
   ```python
   mrs = _build_module_field_results(ev["event_arrays"], module_meta, module_order,
                                     ev["driver_ids"], ev["canonical_key"], task)
   cols = []
   for mr in mrs:  # mrs are in module_order
       if mr.entity_scope == "driver":
           pi_aligned = _align_driver_pi(mr.pi, list(mr.entity_ids), ev["driver_ids"])
       else:
           proj = project_constructor_field_to_drivers(
               mr, driver_ids=ev["driver_ids"], constructor_by_driver=ev["constructor_by_driver"])
           pi_aligned = proj.pi
       cols.append(pi_aligned)   # may be None for driver if a driver missing — then skip event (mirror harness)
   ```
   If any `pi_aligned is None` or projection raises `ValueError`, SKIP that event (the harness's `continue`/`except` behavior) and count it.
7. `M = np.column_stack(cols)`  → `M[:, k]` is module k's pi aligned to `driver_ids`. Season = `int(ev["canonical_key"].split(":")[0])`. Event id = `ev["canonical_key"]`.

## Close Criteria
- `scripts/fusion_replay/metalearner.py` exposes `build_pairwise_dataset(records_dir, task)` (name flexible, documented) returning a dict with at least:
  - `X_delta`: shape `(n_pairs, 4)` — the four module **Δpi = pi_i − pi_j** in `module_names_for_task(task)` order `[constructor_recent, driver_recent, constructor_weekend, driver_weekend]`.
  - `dev_delta`: shape `(n_pairs, 2)` — per-scope **deviation difference** `dev_i − dev_j`, where constructor-scope deviation = `M[:,2] − M[:,0]` (constructor_weekend_pi − constructor_recent_pi, both already projected to drivers) and driver-scope deviation = `M[:,3] − M[:,1]` (driver_weekend_pi − driver_recent_pi). Column 0 = constructor deviation Δ, column 1 = driver deviation Δ.
  - `y`: shape `(n_pairs,)` — 1.0 if entity i finishes ahead of j (`actual_position_i < actual_position_j`), else 0.0.
  - `event_ids`: shape `(n_pairs,)` — canonical event key per pair (for bootstrap-over-events).
  - `seasons`: shape `(n_pairs,)` — int season per pair (for LOSO grouping), from key prefix.
  - a small coverage dict (n_events_used, n_pairs, per-season event counts, n_events_skipped_alignment).
- Pairs emitted once per unordered pair (`i<j` by `driver_ids` order) with **distinct, non-NaN** actual_positions (skip ties and NaN) — mirrors `scoring.pairwise_log_loss`'s `triu_indices(n,k=1)` + valid mask. Do NOT also emit the mirror pair.
- The builder REUSES the harness functions above; it does NOT hand-roll alignment, lineage, or join logic.
- Coverage for **quali** lands near **173 events** (matching #373; Commander smoke-verified exactly 173). If `quali` reaches < ~150 events, STOP and surface it (signals a join/alignment regression). For `race_start`/`race`, generation is still in progress — do NOT assert their counts; the Commander validates them post-generation.

## Allowed Scope
- NEW: `scripts/fusion_replay/metalearner.py`
- NEW: `tests/unit/evo_predictor/test_metalearner.py`
- You MAY import/call any existing `scripts/fusion_replay/*` and `src/evo_predictor/*` functions. The underscore-prefixed scorecard names are importable within the package — import as-is; do NOT refactor scorecard.

## Specific Exclusions
- NO changes to anything under `src/evo_predictor/` (production code frozen).
- NO modelling, CV, or metrics in this gate — data-builder ONLY.
- NO new record-generation logic — records already exist at the dir passed in.
- Do NOT add sklearn.

## Constraints
- `py` not `python`; tests `py -m pytest`.
- `PYTHONIOENCODING=utf-8` MUST be set in the env of ANY python subprocess whose output you capture (records/logs contain non-ASCII; cp1252 pipes fail silently). In PowerShell: `$env:PYTHONIOENCODING='utf-8'` before the call.
- DB is read-only at `C:/Programs/f1Brainz/data` (the harness points there via its own template; you pass nothing).
- Records for the test live at: `outputs/evo_runs/issue-374-records` (relative to worktree root). Use this dir in the test.
- **RECORD GENERATION IS STILL IN PROGRESS (Commander-verified ground truth, do not assume "complete"):** the `quali` task is FULLY generated — all 4 modules (`constructor_quali_power_from_recent_history`, `driver_quali_power_from_recent_history`, `constructor_quali_power_from_race_weekend`, `driver_quali_power_from_race_weekend`) × 8 seasons (2018–2025), and the Commander has SMOKE-VERIFIED that the harness join yields **173 events/quali** with 0 skipped (matches #373). `race_start` and `race` are still being written and may be missing modules right now.
  - **Therefore: write and run your TDD against the `quali` task on the real records dir** — that is your known-good, complete target (assert ~173 events for quali). For `race_start`/`race`, make the builder WORK (call it, assert it returns the documented shape WITHOUT crashing) but do NOT assert a specific event count for them — guard the count assertion to `quali` only, or skip race_start/race if `_load_module_events` returns 0 for any of their 4 modules. The Commander runs the full 3-task coverage check himself once generation completes. Do NOT block on race_start/race coverage.
  - The probe records at `C:/Programs/f1Brainz/.agent-work/archive/2026-06-06-issue-373-correlated-fusion/records_probe/` (driver_quali_recent, race_fail_probe, timing_2024) are available for schema-level sanity but are NOT a complete 4-module set for any task — prefer the real `quali` records for the end-to-end test.
- Antisymmetry note: emit each unordered pair ONCE (`i<j`); do NOT emit the mirror. Model1 will be fit on these rows with binary y — the standard pairwise-logistic setup matching the harness's `triu_indices(n, k=1)`.

## Required Evidence
- `py -m pytest tests/unit/evo_predictor/test_metalearner.py -q` GREEN, output pasted.
- A short stdout dump of the coverage summary for all three tasks (n_events, n_pairs, per-season counts) proving it runs on real records and lands near 173 events/task.

## Verification Commands (PowerShell — this is a Windows box)
```powershell
Set-Location C:/Programs/f1Brainz/.claude/worktrees/agent-ade67b306f11aa4fb
$env:PYTHONIOENCODING='utf-8'
py -m pytest tests/unit/evo_predictor/test_metalearner.py -q
# quali is the complete, known-good target (race_start/race still generating):
py -c "from scripts.fusion_replay.metalearner import build_pairwise_dataset; d=build_pairwise_dataset('outputs/evo_runs/issue-374-records','quali'); print('quali', {k:(v.shape if hasattr(v,'shape') else v) for k,v in d.items() if k in ('X_delta','dev_delta','y')}); print('coverage', d.get('coverage'))"
```

## Suggested Model Tier
stronger — reason: must correctly reuse a subtle existing harness (constructor lineage/projection) and get pairwise/antisymmetry semantics exactly right; errors here silently corrupt the gate.

## Authority
- Target framing (pairwise outcome / pairwise-LL), feature design (Δpi + per-scope deviation), validation strategy are DECIDED by the Commander (see problem_statement.md) — do not redefine.
- You decide: function signatures, internal data structures, how to thread season/event-id, test fixtures.

## Stop Conditions
Stop and return if: you must touch `src/evo_predictor/`; the records dir is missing/empty; `_preprocess_events` cannot be reused without modification; or a task cannot reach ~150+ events (signals a join/alignment problem worth surfacing).

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence produced (paste test output + coverage summary), assumptions used, stop conditions hit, out-of-scope observations.
