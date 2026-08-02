# #670 structural delta — staged for #671 map reconcile (docs/architecture FENCED this run)

Per LAUNCH_ORDER-670 the docs/architecture/* map is FENCED (reconcile is #671). This note stages the
structural changes so #671 folds them into the packet map. This run added **read/run-adapters only** —
no new model, no frozen-constant mint, no stage-logic change.

## New surfaces (all under scripts/ + tests/, epic-659 physics area)
- `scripts/run_season_670.py` — OFFLINE season runner: drives `src/physics/pilot/pipeline.py::run_circuit`
  over the full 2023 season (22-round slate from `get_calendar`, per-round grid from `session_classifications`),
  shared consolidated observables slice via E's INSERT-OR-REPLACE accumulation, per-round FAULT ISOLATION
  (a failing round parks with a diagnosis, never crashes the season), detective vocabulary guard. Pure consumer.
- `scripts/verify_season_artifacts_670.py` — season-run acceptance check (results json + slice non-empty w/ fresh rounds).
- `scripts/run_season_panel_670.py` — the #668 instrument panel over the full corpus; ONLY generalization is the
  cross-circuit split scheme → rotating-block (circle-method) deterministic seed-free balanced split-half, K=n/2
  partitions averaged (imports #668 + `src/physics/instrument_panel/replication.py` rules byte-unchanged).
- `scripts/run_heldout_diagnostic_670.py` — strictly-pre held-out-weekend diagnostic (3 arms: fingerprint×composition,
  driver-overall T7-1 baseline, golf null); composes `src/physics/fingerprint/{join,fit,store}.py` +
  `src/physics/utilization/reference_utilization_store.py`; leakage guards (fit as_of=R-1 internal; golf pool round_idx<R).
- Tests: `tests/unit/physics/pilot/test_season_runner.py`, `tests/unit/physics/instrument_panel/test_panel_corpus.py`,
  `tests/unit/physics/fingerprint/test_heldout_diagnostic.py`.

## Modified surface
- `src/physics/pilot/pipeline.py::run_circuit` — added two keyword run-params forwarded to `run_stage_e`:
  `budget_s` (E per-circuit wall-time; default unchanged E_WALLTIME_BUDGET_S) and `refutil_db` (shared-slice
  override; default None → per-circuit scratch path). Pure plumbing; `run_stage_e` was already accepting both.
  Note (found during the run): `src/data/database.py` is now the package `src/data/database/` (getters in
  `_metadata_session.py`) — a map-anchor update for #671.

## Structural facts worth recording in the map
- The epic-659 chain (C→D→E→G→H→PANEL) is confirmed to run END-TO-END at SEASON SCALE, offline, reproducibly.
- E's car ceiling is built from strictly-prior sessions (`round_idx < R`) → round 1 (and thin round 2) have no
  strictly-prior data and PARK — a real pre-quali property of the pipeline, now handled by per-round isolation.
- The instrument-panel replication decision rules live in `src/physics/instrument_panel/replication.py` and are
  circuit-count-agnostic (`compare_channels_by_class` works on any two halves); only the #668 read-adapter's
  `enumerate_2v2_partitions` was 4-circuit-specific (generalized here as a read-adapter, not a module edit).

## No docs/architecture edit made this run (fenced → #671). Reconcile recorded as a compliant fenced no-op.
