# Implementer Handoff — G3: fusion replay scorecard runner (baseline vs A vs cheap-B)

You are a fresh implementer crew. Work ONLY from this handoff. Repo: f1Brainz (Windows; `py`
not `python`). Branch `constellation/issue-373-correlated-fusion`; cwd = worktree root
(`C:\Programs\f1Brainz\.claude\worktrees\agent-a8cafc9a5b22bcd57`). Set `PYTHONIOENCODING=utf-8`
before EVERY python command (records/logs contain non-ASCII; cp1252 will crash otherwise).

## Context (what already exists — read these first)
The offline fusion-replay harness (G1) and the correlated-fusion variant + R estimator (G2) are
DONE and committed. You are building the SCORECARD RUNNER that ties them to REAL records.

Existing pieces you MUST reuse (do not reimplement their math):
- `scripts/fusion_replay/records.py` — `load_task_records`, `common_driver_ids_for_event`,
  `align_event`. NOTE: `load_task_records` inner-joins on RAW event_id — you must NOT rely on that
  for the cross-module join (see "Event-ID canonicalization" below). You may still use it to load a
  single module, or load via `src.evo_predictor.module_record.load_module_record` directly.
- `scripts/fusion_replay/baseline.py` — `fuse_baseline` (calls production
  `fuse_module_fields_ordered`).
- `scripts/fusion_replay/variants.py` — `run_variant` (calls `fuse_module_fields_correlated`),
  `cheapB_correlation`, `_fuse_baseline_diagonal_numpy`.
- `scripts/fusion_replay/scoring.py` — `pairwise_log_loss`, `rank_mae`, `spearman`,
  `credible_interval_coverage`. USE THESE EXACTLY for metrics.
- `src/evo_predictor/fusion_training/_correlation.py` — `estimate_cross_module_correlation`.
- `src/evo_predictor/fusion_training/_calibration.py` — `module_names_for_task(task)` returns the
  canonical 4-tuple `(constructor_recent, driver_recent, constructor_weekend, driver_weekend)`.
- `src/evo_predictor/fusion.py` — `FusionLayerConfig`, `FusionStepConfig`, `ModuleFieldResult`
  via `src.evo_predictor.runtime_contracts`.
- `src/data/database/manager.py` — `DatabaseManager(db_path=...).get_race_driver_teams(year, round)`
  returns `{driver_id: team_name}` (VERIFIED to match constructor record entity_ids exactly).

Records ALREADY GENERATED (96 files) at:
`.agent-work/issue-373-correlated-fusion/records/<module>__<year>.record.json` (+ .npz sidecars)
for all 12 modules x years 2018..2025. Each record event has `pi`, `sigma_pi`, `entity_ids`,
`target_mu`, `actual_positions`. Per task, 173 events join on the canonical key (verified).

## Gate
g3 (scorecard runner — the measurement engine)

## What to build (exact files)

### 1. `scripts/fusion_replay/scorecard.py` (NEW)
A numpy-only runner that, for each of the 3 tasks (quali, race_start, race):

**(a) Load + canonically join** the 4 module records across ALL years.
- For each module in `module_names_for_task(task)`, load every `<module>__<year>.record.json` in the
  records dir, concatenating events across years.
- Canonicalize each event_id to a join key. Use
  `src.evo_predictor.fusion_training._types.FusionEventKey.from_module_event_id(event_id, task)` and
  key on `str(key)` (year:round:gp:task). Records whose id fails to parse: SKIP + COUNT.
- Inner-join: keep only canonical keys present in ALL 4 modules.

**(b) Per joined event, build the aligned inputs:**
- Driver set = intersection of the two driver-scope modules' entity_ids (use
  `common_driver_ids_for_event`-style logic, or replicate: stable order from first driver module).
  Drop drivers not in all driver modules; COUNT drops.
- `constructor_by_driver`: parse year+round from the canonical key; open
  `DatabaseManager(db_path=f"C:/Programs/f1Brainz/data/f1_data_{year}.db")` and call
  `get_race_driver_teams(year, round)`. Restrict to the event's driver set. If any driver in the set
  is missing from the map, DROP that driver from the set (and COUNT) — never impute a team. If after
  drops <3 drivers remain, SKIP the event (COUNT). Cache the DB handle per year.
- Build a `ModuleFieldResult` for each of the 4 modules from the record arrays (module_name, task,
  entity_scope, evidence_source from module_meta; event_id = the canonical key string; entity_ids,
  pi, sigma_pi from the record event). Constructor modules keep their team entity_ids; driver modules
  their driver entity_ids. (The harness alignment/projection handles the rest.)
- truth arrays aligned to the driver set: `actual_positions` and `target_mu` reordered to the driver
  order (these live on the DRIVER records — use the driver_recent module's per-event arrays, aligned
  by entity_id; assert the two driver modules agree on actual_positions where both present, else
  prefer driver_recent and note).

**(c) Config:** build ONE canonical `FusionLayerConfig` per task:
`FusionLayerConfig(task=task, fusion_order=module_names_for_task(task),
steps=tuple(FusionStepConfig(module_name=m, covariance_scale=1.0, mean_scale=1.0) for m in order),
prior_sigma=10.0, covariance_jitter=1e-6)`. (Commander decision: fixed unit scales so the
A-vs-baseline delta isolates R's effect, no dependence on trained covariance inflation. Document this
in a module docstring.)

**(d) Estimate R** (once per task, pooled over the joined events):
- For each joined event, for each of the 4 modules, compute residual = (module pi aligned to driver
  space) − target_mu, per driver. For constructor modules, project to driver space first (reuse
  `project_constructor_field_to_drivers` via the same alignment you used for fusion, with the event's
  constructor_by_driver). Standardization is done INSIDE `estimate_cross_module_correlation`; you pass
  RAW residual vectors keyed {module_name: (residual_vec, entity_ids=driver_ids)} per event.
- Call `estimate_cross_module_correlation(per_event_residuals, module_order=module_names_for_task(task),
  shrinkage=LAMBDA)`. Default LAMBDA = 0.1. Capture the diagnostics (n_events_used, condition numbers).
- cheap-B R = `cheapB_correlation(R_estimated, module_order, module_meta)`.

**(e) Score 5 variants per event** (all share the same aligned inputs + config):
  1. `baseline` — `fuse_baseline(...)`
  2. `A` — `run_variant(..., correlation=R_estimated)`
  3. `cheapB` — `run_variant(..., correlation=cheapB_R)`
  4. `ablation_RI` — `run_variant(..., correlation=np.eye(4))` (variant A at R=I; sanity)
  5. lambda sweep for A: also compute A at shrinkage in {0.0, 0.25, 0.5, 1.0} (re-estimate R per
     lambda, reuse residuals) — these are extra `A_lambdaXX` variants.
  For each variant's FusedLatentField, compute the 4 metrics with the event's truth:
  pairwise_log_loss(pi, actual_positions), rank_mae(...), spearman(...),
  credible_interval_coverage(pi, sigma_pi, target_mu).

**(f) Aggregate per task:** mean of each metric over events (nanmean; coverage averaged per level
50/80/95). Also compute the PAIRED mean delta (A − baseline) and (cheapB − baseline) per metric
(per-event difference then mean, so it's a paired statistic). Count events scored.

**(g) Output:** write a JSON scorecard to a path given by `--out` (default
`.agent-work/issue-373-correlated-fusion/evidence/scorecard.json`) containing, per task: n_events,
R diagnostics, R_estimated (rounded), per-variant metric means, and paired deltas. Also print a
compact human-readable table to stdout (task x variant x {pairwise_LL, rank_MAE, spearman,
cov50/80/95}).

### 2. `tests/unit/evo_predictor/test_fusion_scorecard.py` (NEW)
Unit tests on SYNTHETIC inputs (no real records, no DB):
- `test_scorecard_RI_equals_baseline_on_diagonal_inputs`: build a tiny synthetic task where each
  module's sigma_pi is DIAGONAL; then variant A at R=I must equal baseline (both reduce to the same
  diagonal precision sum) to atol 1e-9 — proves the runner wires variants correctly. (If you wire
  through full-matrix baseline, instead assert ablation_RI == diagonal-baseline; pick the consistent
  reference and document.)
- `test_scorecard_aggregation_paired_delta`: feed two hand-made events with known per-variant metric
  values via a small monkeypatched scorer, assert the paired delta = mean of per-event diffs.
- `test_canonical_join_drops_unmatched`: two modules with divergent suffixes on the SAME
  year:round:gp canonicalize+join; an event present in only one module is dropped + counted.
- Seed all RNG. Keep it numpy-only + fast.

## Close Criteria (prove each, paste output)
- `py -m pytest tests/unit/evo_predictor/test_fusion_scorecard.py -q` passes.
- `py -m pytest tests/unit/evo_predictor/ -k "fusion or record or replay or scorecard" -q` passes
  (you broke nothing).
- `py -m scripts.fusion_replay.scorecard --records-dir .agent-work/issue-373-correlated-fusion/records --out .agent-work/issue-373-correlated-fusion/evidence/scorecard.json`
  runs to completion over the REAL records and prints the table for all 3 tasks with non-degenerate
  numbers (baseline pairwise_LL in a plausible 0.5..3 range, spearman in [-1,1], coverage in [0,1]).
  Paste the printed table + confirm scorecard.json was written.
- `py -m src.utils.simplification_limits --paths scripts/fusion_replay/scorecard.py tests/unit/evo_predictor/test_fusion_scorecard.py` passes (split helpers if flagged).
- Sanity: in the printed numbers, `ablation_RI` (A at R=I) must NOT outperform/underperform wildly vs
  what you'd expect; and A vs baseline deltas must be FINITE for all 3 tasks. Report any task where A
  fails to estimate R (e.g. condition number explosion) explicitly rather than hiding it.

## Allowed Scope
- CREATE: `scripts/fusion_replay/scorecard.py`, `tests/unit/evo_predictor/test_fusion_scorecard.py`.
- READ: anything under src/ and scripts/fusion_replay/.
- You MAY add a tiny private helper module under scripts/fusion_replay/ if scorecard.py would exceed
  simplification limits (e.g. `scripts/fusion_replay/_scorecard_io.py`) — keep it numpy-only.
- Do NOT modify fusion.py, _correlation.py, variants.py, records.py, scoring.py, baseline.py, or any
  production code. Do NOT regenerate records. Do NOT touch docs (the commander writes the findings).

## Specific Exclusions
- No training. No FastF1 calls. DB is READ-ONLY via the per-year absolute paths.
- Do NOT flip any production call-site. Do NOT enter #374 interaction-modelling territory.

## Constraints
- numpy-only (scipy via the existing scoring module is fine). PYTHONIOENCODING=utf-8.
- Missingness EXPLICIT: count every skipped event / dropped driver / unparseable id / missing team /
  missing target_mu; surface counts in the scorecard JSON + printed summary. NEVER impute.
- One canonical path; explicit input validation (name field/expected/actual on errors).
- DB handles: open per-year once, reuse; do not leak file handles (close or use context).

## Suggested Model Tier
sonnet (integration-heavy; alignment + canonical join + DB mapping need care).

## Stop Conditions
Stop and return if: real-record run cannot produce finite metrics for a task and you cannot determine
why within scope (report the failure + diagnostics); the canonical join yields 0 events for a task
(report which key parsing failed); or a close criterion cannot be met without touching production code.

## Return Format
Return IMPLEMENTER_RESULT: files created (full paths), the pytest tails, the FULL printed scorecard
table (all 3 tasks, all variants, all metrics) and the path to scorecard.json, the R diagnostics per
task (n_events_used, condition numbers, the estimated R off-diagonals for the constructor<->driver
block), all missingness counts, assumptions, stop conditions hit, out-of-scope observations.
DO of NOT write any findings/verdict prose — that is the commander's job. Just the runner + numbers.
