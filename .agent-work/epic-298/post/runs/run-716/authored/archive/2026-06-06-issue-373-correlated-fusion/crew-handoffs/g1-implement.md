# Implementer Handoff — G1: Offline fusion-replay harness + baseline reproduction

You are a fresh implementer crew. Work ONLY from this handoff. Repo: f1Brainz (Windows;
Python launcher is `py`, never `python`). You are on branch
`constellation/issue-373-correlated-fusion` in a git worktree; cwd is the worktree root.
Set `PYTHONIOENCODING=utf-8` in any shell that runs python (cp1252 console).

## Gate
g1

## Task
Build a numpy-only, reusable **offline fusion-replay harness** as an importable package
under `scripts/`, plus an automated test that proves the harness's BASELINE reproduces the
real production fusion `fuse_module_fields_ordered` to numerical tolerance (<=1e-9). This
gate does NOT need real record files — validate with a SYNTHETIC fixture. Later gates add
variant A and run it over real records.

## Background you need (do not go spelunking beyond these)
- Production fusion: `src/evo_predictor/fusion.py`, function `fuse_module_fields_ordered(
  module_results, *, driver_ids, constructor_by_driver, config)`. It does a sequential
  per-entity Gaussian precision update over the task's modules:
  start posterior_mean=0, posterior_cov=I*(prior_sigma**2) (prior_sigma=10 default);
  for each enabled module (in `config.fusion_order`): align/project to driver space, form
  `obs_cov = covariance_scale*observation.sigma_pi + jitter*I + tension_inflation*I`, then
  `posterior_precision = prior_precision + obs_precision`,
  `posterior_mean = posterior_cov @ (prior_precision@prior_mean + obs_precision@obs_mean)`.
  Read the function to get exact details. It returns a `FusedLatentField` (pi, sigma_pi).
- Inputs to that function are `ModuleFieldResult` objects defined in
  `src/evo_predictor/runtime_contracts.py` (fields: module_name, task, entity_scope
  {driver|constructor}, evidence_source {recent_history|race_weekend}, event_id,
  entity_ids: tuple[str], pi: (n,) float, sigma_pi: (n,n) symmetric float, diagnostics:
  dict). Validation is strict (pi finite 1D, sigma_pi symmetric to 1e-10, entity_ids unique).
- Config: `FusionLayerConfig(task, fusion_order: tuple[str], steps: tuple[FusionStepConfig],
  prior_sigma=10.0, covariance_jitter=1e-6)` and
  `FusionStepConfig(module_name, covariance_scale=1.0, mean_scale=1.0, enabled=True,
  covariance_tension_inflation=0.0)`. Read `fusion.py` for exact constructors.
- Constructor projection: `src/evo_predictor/constructor_projection.py`
  `project_constructor_field_to_drivers(constructor_result, *, driver_ids,
  constructor_by_driver)` — copies a constructor's pi/cov rows to each driver. The real
  fusion calls this for constructor-scope modules.
- Record IO (already exists, REUSE — do not reimplement): `src/evo_predictor/module_record.py`
  `load_module_record(index_path_or_stem) -> dict` with key `"events"`: list of per-event
  dicts each carrying numpy arrays `pi (n,)`, `sigma_pi (n,n)`, `outcome (pairs,)`,
  `pair_index (pairs,2)`, `features (pairs,d)`, `dqi (pairs,)`, `entity_ids: list[str]`,
  and optional `target_mu (n,)` / `actual_positions (n,)` (None when absent), plus index
  fields `module_name, task, entity_scope, evidence_source, event_id`. Schema doc:
  `docs/evo/module_backtest_record.md`.
- The 4 modules of a task, in canonical order, come from `module_names_for_task(task)` in
  `src/evo_predictor/fusion_training/_calibration.py`:
  `(constructor_{tok}_from_recent_history, driver_{tok}_from_recent_history,
    constructor_{tok}_from_race_weekend, driver_{tok}_from_race_weekend)`,
  tok in {quali_power, race_start_power, race_power}. You may import this helper.

## What to build (exact files)
Create package `scripts/fusion_replay/` with:

1. `scripts/fusion_replay/__init__.py` — exports the public API below.

2. `scripts/fusion_replay/records.py` — loading + alignment (numpy + stdlib only):
   - `load_task_records(record_paths: Mapping[str,str], task: str) -> dict` — given a map
     {module_name -> record index .json path} for the 4 modules of `task`, load each via
     `load_module_record`, index events by `event_id`, and return a structure that lets you
     iterate events present in ALL 4 modules (inner join on event_id). For each joined event
     expose, per module: pi, sigma_pi, entity_ids, target_mu, actual_positions.
   - `align_event(module_event_arrays, driver_ids) -> ...` — align each module's per-entity
     arrays to a common entity ordering. DRIVER modules align directly by entity_id;
     CONSTRUCTOR modules are entity_scope='constructor' (entity_ids are constructor ids) and
     must be projected to driver space (you may call `project_constructor_field_to_drivers`,
     OR document that record-based replay supplies driver-space arrays — see note below).
   - **Entity-set note (IMPORTANT):** different events/modules have different/disjoint
     entity sets. Choose the common driver set for an event as the intersection of the
     driver-scope modules' entity_ids; require constructor coverage for all those drivers.
     Represent any dropped entity EXPLICITLY (return counts/ids of dropped entities); never
     silently impute. If you cannot derive `constructor_by_driver` from records alone,
     accept it as an argument and document the requirement; do NOT guess a mapping.

3. `scripts/fusion_replay/baseline.py` — the baseline fusion the harness trusts:
   - `fuse_baseline(module_results, *, driver_ids, constructor_by_driver, config)` — this
     must produce the SAME (pi, sigma_pi) as the real `fuse_module_fields_ordered`. The
     cleanest correct approach: **call the real function** and return its FusedLatentField
     (so "reproduce" is identity by construction) — that is acceptable and preferred for the
     baseline, since the real function is already numpy. ALSO provide an independent numpy
     re-derivation `_fuse_baseline_numpy(...)` used ONLY by the test to confirm your
     understanding matches to <=1e-9. The point: the harness baseline == production fusion,
     provably.

4. `scripts/fusion_replay/scoring.py` — numpy-only metrics on a fused field vs truth:
   - `pairwise_log_loss(pi, actual_positions) -> float` — over all unordered entity pairs
     (i<j) with distinct actual positions: model prob that i beats j (finishes ahead, i.e.
     lower position number) = sigmoid(pi_i - pi_j); label = 1 if actual_position_i <
     actual_position_j else 0; return mean of -[y*log p + (1-y)*log(1-p)] with eps clipping.
   - `rank_mae(pi, actual_positions) -> float` — convert pi to ranks (higher pi = rank 1 =
     predicted-best, matching the convention that lower actual position is better), convert
     actual_positions to ranks, return mean absolute rank difference.
   - `spearman(pi, actual_positions) -> float` — Spearman rank correlation between pi
     (descending = better) and actual_positions (ascending = better); be explicit about
     sign so a perfect predictor scores +1.
   - `credible_interval_coverage(pi, sigma_pi, target_mu, levels=(0.5,0.8,0.95)) -> dict` —
     for each entity, central interval pi_i +/- z(level)*sqrt(sigma_pi_ii); coverage =
     fraction of entities with target_mu_i in the interval; return {level: coverage} and
     {level: coverage - level} (coverage error). Use scipy.stats.norm.ppf OR a small inline
     z-table; numpy/scipy only.
   - All metrics must handle the empty/degenerate case by returning NaN with no crash, and
     must skip entities/pairs with missing truth EXPLICITLY (document the skip).

5. `tests/unit/evo_predictor/test_fusion_replay_harness.py` — the validation gate:
   - **test_baseline_reproduces_real_fusion**: build a SYNTHETIC task with 4
     `ModuleFieldResult`s (2 driver-scope, 2 constructor-scope) for one event with a small
     driver set (e.g. 5 drivers, 3 constructors), random-but-seeded pi and SPD sigma_pi,
     a `FusionLayerConfig` with non-trivial per-module covariance_scale. Call the real
     `fuse_module_fields_ordered` and your `_fuse_baseline_numpy`; assert
     `np.allclose(real.pi, mine.pi, atol=1e-9)` and same for sigma_pi. This proves the
     harness baseline is faithful.
   - **test_scoring_sanity**: a perfectly-ordered pi vs actual_positions gives spearman==1,
     rank_mae==0, and lower pairwise_log_loss than a reversed pi; coverage of a tight
     interval around target_mu==pi is ~1.0. Keep assertions tolerance-based.
   - Make SPD covariances via `A@A.T + k*I`. Seed all RNG. No real data, no DB, no network.

## Close Criteria (you must prove each)
- `py -m pytest tests/unit/evo_predictor/test_fusion_replay_harness.py -q` passes.
- The baseline test genuinely calls the REAL `fuse_module_fields_ordered` and matches an
  INDEPENDENT numpy re-derivation to <=1e-9 (not a self-comparison tautology).
- Package is numpy/scipy/stdlib only (no torch, no DB, no FastF1, no network).
- `py -m src.utils.simplification_limits scripts/fusion_replay tests/unit/evo_predictor/test_fusion_replay_harness.py` passes (run it; fix or split files if it flags).
- No production source behavior changed (you may READ src/evo_predictor/*; you only ADD new
  files under scripts/fusion_replay/ and the one test file).

## Allowed Scope
- CREATE: `scripts/fusion_replay/*.py`, `tests/unit/evo_predictor/test_fusion_replay_harness.py`.
- READ (do not modify): anything under `src/evo_predictor/`.

## Specific Exclusions
- Do NOT modify `src/evo_predictor/fusion.py` or any production source in this gate.
- Do NOT implement variant A / correlated R / cheap-B yet (that is G2).
- Do NOT generate or require real record files.
- Do NOT touch quali-head / latent_power code, or any docs.

## Constraints
- numpy-only harness (scipy.stats allowed for norm.ppf; stdlib allowed). No torch import.
- Validate meaningful inputs with messages naming field + expectation + actual.
- Missingness explicit (return dropped-entity/pair counts), never silent imputation.
- One canonical path; no compatibility shims.

## Verification Commands
```
py -m pytest tests/unit/evo_predictor/test_fusion_replay_harness.py -q
py -m src.utils.simplification_limits scripts/fusion_replay tests/unit/evo_predictor/test_fusion_replay_harness.py
```

## Suggested Model Tier
sonnet (bounded; numerics need care on the baseline identity).

## Authority
Decisions already made by the commander (do not re-litigate): baseline validation = exact
reproduction of `fuse_module_fields_ordered` (the gold scalar report metric is NOT the
gate); 4-module canonical order from `module_names_for_task`; harness is numpy-only under
scripts/. If `constructor_by_driver` cannot be derived from records, accept it as a
parameter and document — do not invent a mapping.

## Stop Conditions
Stop and return if: you must modify production source to make the baseline match (means your
re-derivation is wrong — report what mismatches), the real function cannot be imported, or a
close criterion cannot be met. Do not exceed allowed scope.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed (full paths), test mode satisfied,
exact verification command outputs (paste the pytest + simplification_limits tail),
assumptions used, stop conditions hit, out-of-scope observations.
