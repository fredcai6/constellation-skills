# Gated Plan: `issue-253-curriculum-holdout`

## Problem Statement

Complete the remaining prerequisites for a coherent gold-cycle training run that demonstrates progress on the #253 training curriculum. This covers artifact naming cleanup (#275), compound prior regeneration (#277), recent-history holdout diagnostic modes (#253), time-gap/calendar features as model inputs (#209), calendar-dependent holdout modes, and the gold training run itself (2018–2024 train / 2025 eval).

## Intent Protected

- Gold cycle runs cleanly with 2018–2024 train / 2025 eval, produces legible artifacts, and includes holdout diagnostics showing model behaviour by evidence recency
- Time-gap/calendar features are live as model inputs before the run — not just diagnostic slicers
- Compound priors are regenerated from the canonical path for all available seasons
- No partial or misnamed artifacts in params/gold/

## Scope

**Allowed regions/files:**
- `src/evo_predictor/gold_cycle/` — slug utility, runner wiring, schema
- `src/evo_predictor/module_training_orchestration.py` — holdout mode eval batches
- `src/evo_predictor/recent_history_adapter.py` and all `*_recent_history_adapter.py` variants — time-gap feature addition
- `src/evo_predictor/driver_residual_history_adapter.py` — time-gap features
- `fusion_training.py` — slug update
- `scripts/assemble_trained_sampled_runtime_manifest.py` — slug update
- `params/gold/fusion/` and `params/gold/uncertainty_calibration/` — git mv committed artifact renames
- `params/gold/compound_prior/` — promote new artifacts
- `tests/unit/evo_predictor/` — fixture updates for renaming + new feature tests
- `configs/evo/gold_defaults.toml` — read-only reference; no changes unless required
- `src/data/database.py` — read-only reference; new `get_round_event_dates()` accessor only if needed

**Not scope:**
- #270 Q leakage fix (training-time eligible_drivers) — deferred, low priority
- #211 calibration by mode — sequenced after stable artifacts from this run
- #265 Gaussian mixture fusion — future work
- #255 learned gates — future work
- 2026 eval year — not yet

**Specific exclusions:**
- Do not change gold_defaults.toml train/eval config (2018–2024 / 2025 stays fixed)
- Do not change JSON payload schemas or internal field names
- Do not add backward-compat aliases for old artifact filenames — clean break
- Do not add exotic #209 features (driver_constructor_pair_continuity, reserve/substitute indicators)

## Structural Baseline

**Need:** no  
**Status:** skipped — prior conversation established a thorough read-only survey of the relevant modules; no Cartographer baseline needed for this scope  
**Evidence:** `module_training_orchestration.py` evidence_mode_metrics wiring confirmed; `event_date` confirmed in DB sessions table; feature dim is data-driven via `feature_names` lists; `gold_report_schema.py` schema confirmed; committed artifact paths in `params/gold/` confirmed

## Authority / Assumptions

- `train_years = [2018..2024]`, `eval_year = 2025` — user confirmed, do not change
- #270 deferred — user decision
- #277 is data-prep only (no source changes), run before Gate 6
- Gate 2 has a hard stop: if any season's compound prior cannot be verified complete, halt and surface to user before proceeding
- Time-gap features: minimal set only — `days_since_prior_race`, `season_boundary_flag`, `same_season_flag`, `early_season_round_index`; all sourced from `event_date` in DB
- #275 goes in before the training run or is dropped from this effort — user decision
- Holdout modes are evaluation-only diagnostic slices on 2025 eval; no retraining per mode
- Feature dim changes invalidate existing checkpoints — fine, we're doing a fresh run

## Test Mode

**Plan default:** TDD for all behavior changes (new features, new diagnostic modes, slug utility)  
**Data-run gates (Gate 2):** evidence is script output + artifact verification, not unit tests

## Project Mechanics Hooks

| Moment | Hook | Owner | Evidence |
|---|---|---|---|
| Before each code gate | branch off main, worktree | Pilot | branch name / worktree |
| After gate evidence accepted | commit + PR to main | Crew implementer | commit SHA / PR URL |
| After Gate 2 (data run) | verify + stop if incomplete | Pilot | verification output |
| Before Gate 6 | confirm all prior gates merged | Pilot | git log check |
| Before closeout | archive `.agent-work/issue-253-curriculum-holdout/` | Pilot | archive path |
| After archive | commit archived workflow artifacts | Pilot | commit SHA |

---

## Gates

### Gate 1: Artifact naming cleanup (#275)

**Purpose:** Standardise all gold-cycle artifact filenames to `<artifact_id>_<YYMMDD_HHMMSS>_<short_descriptor>` before the training run produces new artifacts with the correct names.

**Crew cycle:** implementer Crew → integrate evidence → reviewer Crew → integrate evidence → gate close  
**Implementer handoff:** required  
**Reviewer handoff:** required — touches committed params files and 4 test files; risk of silent regression  
**Suggested model tier:** simple bounded — well-specified mechanical rename with clear acceptance criteria  
**Test mode:** same as plan (TDD — update tests to match new convention, confirm all pass)  
**Allowed scope:** `src/evo_predictor/gold_cycle/` (new slug.py + runner.py), `src/evo_predictor/fusion_training.py`, `scripts/assemble_trained_sampled_runtime_manifest.py`, `params/gold/fusion/`, `params/gold/uncertainty_calibration/`, `tests/unit/evo_predictor/` (4 test files listed in issue)  
**Specific exclusions:** do not change JSON payload field names; do not rename `outputs/` or `reports/evo/` (gitignored, transient)

**Implementation checklist:**
- [ ] Create `src/evo_predictor/gold_cycle/slug.py` with `make_artifact_slug(artifact_id, run_start_dt, descriptor) -> str`
- [ ] Update `runner.py:171–172` (`slug`) to use `make_artifact_slug("gold_cycle", ...)`
- [ ] Update `runner.py:288–289` (`diagnostics_slug`) to use `make_artifact_slug("unc_diag", ...)`
- [ ] Update `fusion_training.py:457–458` stem to use `make_artifact_slug("fusion", ...)`
- [ ] Update `scripts/assemble_trained_sampled_runtime_manifest.py` (4 path-builder functions) to use new convention
- [ ] `git mv params/gold/fusion/static_hierarchical_fusion_*.json` → new names (3 files)
- [ ] `git mv params/gold/uncertainty_calibration/module_uncertainty_calibration_*.json` → new names (5 files)
- [ ] Update `tests/unit/evo_predictor/test_pipeline_validation.py` (15+ stem references)
- [ ] Update `tests/unit/evo_predictor/test_runtime_bundle_materialization.py` (2 fusion config path refs)
- [ ] Update `tests/unit/evo_predictor/test_gold_runtime_bundle_schema_alignment.py` (1 path ref)
- [ ] Update `tests/unit/evo_predictor/test_sampled_runtime_comparison_manifest_resolution.py` (1 stem ref)
- [ ] Update docstring in `scripts/materialize_runtime_bundles.py`
- [ ] Update comment in `src/evo_predictor/runtime_bundle_materializer.py:50`

**Close criteria:**
- [ ] `make_artifact_slug` utility exists and is the single slug-generation callsite
- [ ] All 5 artifact types produce `<artifact_id>_<YYMMDD_HHMMSS>_<short_descriptor>` filenames
- [ ] Committed params artifacts renamed via `git mv` (verified with `git status`)
- [ ] `py -m pytest tests/unit/evo_predictor/` passes with zero failures
- [ ] Reviewer confirms no hardcoded old-convention stems remain in source

**Required evidence:**
- `py -m pytest tests/unit/evo_predictor/ -v` — zero failures
- `git diff --stat HEAD` showing renamed params files and updated test stems
- Reviewer diff inspection of slug.py and all updated callsites

**Stop conditions:** any test failure that can't be resolved by updating the fixture stems; any ambiguity about which committed artifact maps to which new name  
**Next gate:** Gate 2

---

### Gate 2: Compound prior regeneration (#277) — data run

**Purpose:** Regenerate gold compound-prior artifacts for 2018–2025 from the canonical unified solver path (`fit_tire_wear_model` + `promote_runtime_artifact`), replacing the existing exploratory-path artifacts. Hard stop if any season is incomplete.

**Crew cycle:** implementer Crew (script execution + verification) → integrate evidence → reviewer skipped (data run, not code change) → gate close  
**Implementer handoff:** required  
**Reviewer handoff:** skipped — no source changes; evidence is artifact existence + validation output  
**Suggested model tier:** simple bounded — script execution with explicit verification steps  
**Test mode:** not applicable (data run) — evidence is `validate_tire_wear_fit.py` output + `load_compound_prior_artifact` spot checks  
**Allowed scope:** `params/gold/compound_prior/`, `outputs/tire_wear_run/` (transient), script execution only  
**Specific exclusions:** do not modify any source files; do not promote artifacts from seasons with validation failures

**Execution checklist:**
- [ ] For each target season (2018–2025), run `fit_tire_wear_model` to produce bundle in `outputs/tire_wear_run/<year>/`
- [ ] For each season, run `scripts/validate_tire_wear_fit.py` — capture output; **STOP if any season reports insufficient data or validation failure**
- [ ] Surface any seasons with missing/incomplete lap data to user before proceeding
- [ ] After all seasons validated, run `promote_runtime_artifact` for each to `params/gold/compound_prior/`
- [ ] Spot-check each promoted artifact: `load_compound_prior_artifact(path)` succeeds
- [ ] Confirm no same-season leakage in any artifact (leakage check in validate script)
- [ ] Run `tests/integration/test_compound_prior_real_data_smoke.py` with expanded year list

**Close criteria:**
- [ ] `params/gold/compound_prior/<year>/compound_prior_summary.json` exists for each validated season (2018–2025, skipping any with insufficient data)
- [ ] All promoted artifacts pass `load_compound_prior_artifact` without error
- [ ] `validate_tire_wear_fit.py` output captured and attached as evidence for each season
- [ ] Integration smoke test passes

**Required evidence:**
- Validation output for each season (pass/fail + data coverage stats)
- `ls params/gold/compound_prior/` listing showing new artifacts
- Integration test run output

**Stop conditions:**
- Any season validation failure → halt, report to user, do not promote partial artifacts
- Missing lap data for a season → report which seasons are affected; user decides whether to collect data first or proceed with available seasons

**Next gate:** Gate 3

---

### Gate 3: Round/year-based holdout diagnostic modes

**Purpose:** Add evaluation-only diagnostic slicing to the gold cycle for `same_season_recent` (early-season rounds with limited within-season history) and `race_holdout` (per-round metric breakdown). These use only year/round_num data — no calendar dates required.

**Crew cycle:** implementer Crew → integrate evidence → reviewer Crew → integrate evidence → gate close  
**Implementer handoff:** required  
**Reviewer handoff:** required — new diagnostic path wired into gold cycle runner; schema changes  
**Suggested model tier:** simple bounded — well-defined by analogy with existing `evidence_mode_metrics` pattern  
**Test mode:** same as plan (TDD)  
**Allowed scope:** `src/evo_predictor/module_training_orchestration.py`, `src/evo_predictor/gold_cycle/runner.py`, `src/evo_predictor/gold_report_schema.py`, `tests/unit/evo_predictor/`  
**Specific exclusions:** do not touch race_weekend evidence mode logic; do not change training code

**Implementation checklist:**
- [ ] Add `build_recent_history_holdout_eval_batches(module_name, manifest_path, eval_year, db_path, db_root, ...)` in `module_training_orchestration.py`
  - `same_season_recent`: filter eval rounds to first `N` rounds of the season (rounds where within-season race count ≤ threshold, e.g. ≤ 5); evaluate against full-evidence backtest
  - `race_holdout`: per-round metric breakdown — group eval pairs by round_num, report metrics per round
- [ ] Wire into `runner.py` for all `recent_history` modules (analogous to `_run_evidence_mode_eval` for race_weekend modules)
- [ ] Add `recent_history_holdout_metrics` field to `gold_report_schema.py` with schema doc
- [ ] Tests: correct round filtering; empty-set handling (graceful no-op); schema field present in report

**Close criteria:**
- [ ] `build_recent_history_holdout_eval_batches` returns correctly filtered batches for both modes
- [ ] Gold cycle runner populates `recent_history_holdout_metrics` in the report JSON
- [ ] `gold_report_schema.py` documents the new field
- [ ] `py -m pytest tests/unit/evo_predictor/ -v` passes
- [ ] Reviewer confirms filtering logic is round/year-only (no date arithmetic)

**Required evidence:**
- `py -m pytest tests/unit/evo_predictor/ -v` — zero failures
- Smoke run confirming `recent_history_holdout_metrics` appears in report JSON output
- Reviewer diff inspection of filtering logic

**Stop conditions:** ambiguity about what constitutes "early season" threshold (expose as config, default 5); any test failure in filtering logic  
**Next gate:** Gate 4

---

### Gate 4: Time-gap and calendar features as model inputs (#209 minimal set)

**Purpose:** Add `days_since_prior_race`, `season_boundary_flag`, `same_season_flag`, and `early_season_round_index` as real model inputs to all recent-history modules, sourced from `event_date` in the DB. These features teach the model to discount stale evidence.

**Crew cycle:** implementer Crew → integrate evidence → reviewer Crew → integrate evidence → gate close  
**Implementer handoff:** required  
**Reviewer handoff:** required — feature vector contract change; time-safety is critical  
**Suggested model tier:** stronger broad — touches 5–6 adapter modules, new DB query, time-safety constraints  
**Test mode:** same as plan (TDD — time-safety tests are acceptance criteria, not optional)  
**Allowed scope:** `src/evo_predictor/recent_history_adapter.py`, `src/evo_predictor/quali_recent_history_adapter.py`, `src/evo_predictor/constructor_race_recent_history_adapter.py`, `src/evo_predictor/constructor_quali_recent_history_adapter.py`, `src/evo_predictor/race_start_recent_history_adapter.py`, `src/evo_predictor/driver_residual_history_adapter.py`, `src/data/database.py` (new read accessor only), `tests/unit/evo_predictor/`  
**Specific exclusions:** do not change race_weekend or race_power adapters; do not add exotic features (pair continuity, substitute flags); do not change model architecture (feature dim is data-driven)

**Feature definitions:**
- `days_since_prior_race`: days between this round's race date and the prior round's race date in the DB; 0 for round 1 of a season (or a large sentinel like 365.0)
- `season_boundary_flag`: 1.0 if this is the first round of a new season, 0.0 otherwise
- `same_season_flag`: 1.0 if the prior race in the history window is from the same season, 0.0 if prior season
- `early_season_round_index`: normalised round index within season (round_num / total_season_rounds, 0.0–1.0); signals how early in the season we are

**Implementation checklist:**
- [ ] Add `get_round_event_date(year, round_num) -> date | None` to `DatabaseManager` (query `sessions` table by year + round_num + session_type='R', return `event_date`)
- [ ] Add shared helper `compute_recency_features(current_year, current_round_num, db_manager) -> RecencyFeatureRow` (or inline in each adapter) that returns the 4 values above using only prior-round dates
- [ ] Add `days_since_prior_race`, `season_boundary_flag`, `same_season_flag`, `early_season_round_index` to the `_FEATURE_NAMES` list in each of the 6 recent-history adapter modules
- [ ] Compute and append these values to the feature vector in each adapter's batch-building function
- [ ] Write time-safety tests: assert that computing features for round N uses only rounds < N; no future dates; round 1 sentinel handled correctly
- [ ] Write missingness tests: graceful fallback when DB has no prior round date (e.g. 2018 round 1)
- [ ] Run `py -m pytest tests/unit/evo_predictor/ -v` — zero failures
- [ ] Run smoke training on a single module with `--max-rounds-per-year 3` to confirm new feature dim is accepted

**Close criteria:**
- [ ] All 6 recent-history adapters emit 4 additional features per pair (feature dim increases by 4)
- [ ] `assert_pair_batch` calls pass with updated expected_feature_dim
- [ ] Time-safety tests pass: no future round dates used
- [ ] Missingness/sentinel tests pass
- [ ] Smoke training on 1 module completes without error
- [ ] Reviewer confirms time-safety logic and no feature leakage

**Required evidence:**
- `py -m pytest tests/unit/evo_predictor/ -v` — zero failures
- Smoke run output showing training completes with new feature dim
- Reviewer diff inspection with focus on time-safety in the helper and all 6 adapters

**Stop conditions:** DB missing `event_date` for a significant fraction of rounds (surface to user); disagreement on sentinel value for round 1 (document decision in code comment and proceed)  
**Next gate:** Gate 5

---

### Gate 5: Calendar-dependent holdout diagnostic modes

**Purpose:** Add `short_gap_holdout` and `season_boundary_holdout` diagnostic slices to the gold cycle. These require `event_date` from the DB (available after Gate 4's infrastructure is in) to partition the 2025 eval rounds by calendar gap type.

**Crew cycle:** implementer Crew → integrate evidence → reviewer Crew → integrate evidence → gate close  
**Implementer handoff:** required  
**Reviewer handoff:** required — date arithmetic must be time-safe  
**Suggested model tier:** simple bounded — follows Gate 3 pattern exactly; date source already established  
**Test mode:** same as plan (TDD)  
**Allowed scope:** `src/evo_predictor/module_training_orchestration.py`, `src/evo_predictor/gold_cycle/runner.py`, `src/evo_predictor/gold_report_schema.py`, `tests/unit/evo_predictor/`  
**Specific exclusions:** do not change feature computation; do not retrain models

**Mode definitions:**
- `short_gap_holdout`: eval rounds where `days_since_prior_race` ≤ 8 (back-to-back or triple header rounds); default threshold configurable
- `season_boundary_holdout`: eval rounds that are round 1–3 of a season (season opener through third round)

**Implementation checklist:**
- [ ] Extend `build_recent_history_holdout_eval_batches` from Gate 3 to add `short_gap_holdout` and `season_boundary_holdout` modes
- [ ] Implement date-based round filtering using `get_round_event_date` from Gate 4
- [ ] Confirm `recent_history_holdout_metrics` in report schema covers these two new mode keys (update schema doc)
- [ ] Tests: correct round filtering by day gap threshold; correct season-boundary detection; empty-set handling
- [ ] Time-safety check: mode filtering uses only prior-round dates for gap computation (same helper as Gate 4)

**Close criteria:**
- [ ] `short_gap_holdout` correctly identifies back-to-back rounds (≤ 8 day gap)
- [ ] `season_boundary_holdout` correctly identifies rounds 1–3 of the eval season
- [ ] Both modes appear in the gold report `recent_history_holdout_metrics` JSON
- [ ] `py -m pytest tests/unit/evo_predictor/ -v` passes
- [ ] Reviewer confirms date arithmetic is correct and time-safe

**Required evidence:**
- `py -m pytest tests/unit/evo_predictor/ -v` — zero failures
- Smoke run confirming both new mode keys appear in report JSON
- Reviewer diff inspection of date filtering

**Stop conditions:** insufficient `event_date` coverage in DB to identify gap rounds for 2025 eval season (surface to user)  
**Next gate:** Gate 6

---

### Gate 6: Gold training run (2018–2024 / 2025 eval)

**Purpose:** Execute the full gold cycle with all new features and diagnostics live. Produce report artifacts with the new naming convention, compound priors from Gate 2, time-gap features from Gate 4, and all four holdout diagnostic modes from Gates 3 and 5.

**Crew cycle:** implementer Crew (run execution + report capture) → integrate evidence → reviewer Crew (report review) → integrate evidence → gate close  
**Implementer handoff:** required  
**Reviewer handoff:** required — review report for obvious anomalies, metric regressions, and naming correctness  
**Suggested model tier:** simple bounded — run execution; no code changes; review is report inspection  
**Test mode:** not applicable — evidence is report output and metric sanity checks  
**Allowed scope:** `outputs/evo_runs/gold_module_training_cycle/`, `reports/evo/`, `params/gold/` (read-only); no source changes  
**Specific exclusions:** do not change gold_defaults.toml; do not merge partial or failed run outputs

**Pre-run checklist:**
- [ ] Confirm Gates 1–5 are all merged to main
- [ ] Confirm compound priors exist for all required seasons (`params/gold/compound_prior/<year>/`)
- [ ] Confirm `configs/evo/gold_defaults.toml` is unchanged (2018–2024 / 2025)
- [ ] Confirm DB files exist for all train years + eval year

**Run checklist:**
- [ ] Run gold cycle: `py -m src.evo_predictor gold-cycle --config configs/evo/gold_defaults.toml`
- [ ] Monitor for any early-termination errors; capture full log
- [ ] Confirm all module manifests written to `outputs/evo_runs/gold_module_training_cycle/`
- [ ] Confirm sampled runtime manifest assembled
- [ ] Confirm LOSO fusion calibration ran

**Verification checklist:**
- [ ] Report JSON exists: `gold_cycle_<YYMMDD_HHMMSS>_2018thru2024.summary.json` (new naming)
- [ ] `evidence_mode_metrics` is non-empty in report (race_weekend modules)
- [ ] `recent_history_holdout_metrics` is non-empty (all 4 modes: `same_season_recent`, `race_holdout`, `short_gap_holdout`, `season_boundary_holdout`)
- [ ] No NaN metrics in top-level module metrics (pairwise log loss, Brier, Spearman)
- [ ] Sampled runtime manifest round-trip test passes: `py -m pytest tests/unit/evo_predictor/test_sampled_runtime_comparison_manifest_resolution.py`
- [ ] Run `py -m pytest tests/` — full suite green

**Reviewer checklist:**
- [ ] Metrics are in plausible range (pairwise log loss < 0.7, Spearman > 0.2 for race modules)
- [ ] No unexpected module failures or empty event counts
- [ ] New artifact names are legible and timestamp-stamped
- [ ] Holdout mode metrics show expected pattern (e.g. `season_boundary_holdout` has higher uncertainty / worse metrics than overall — this is expected and healthy)

**Close criteria:**
- [ ] Full run completes without error
- [ ] All verification checks pass
- [ ] Reviewer signs off on metric plausibility and naming correctness

**Required evidence:**
- Full run log (stdout/stderr capture)
- Report JSON path + `recent_history_holdout_metrics` excerpt
- `py -m pytest tests/` output
- Reviewer notes on metric plausibility

**Stop conditions:** any module training failure; zero usable events for a module; NaN metrics in report; naming convention not matching Gate 1 output  
**Next gate:** closeout

---

## Triage Candidate Log

| Candidate | Reason | Anchor | Evidence | Status |
|---|---|---|---|---|
| #211 calibration by mode | sequenced after stable artifacts; not started | Gate 6 report | n/a | noted — route to issue after Gate 6 |
| #270 Q leakage fix (training) | deferred by user decision; low priority | plan authority | issue #270 | noted — keep open |

---

## Plan-Level Stop Conditions

- Gate 2 compound prior validation fails for any season → halt, surface to user
- Gate 4 DB missing `event_date` for significant fraction of rounds → halt, surface to user
- Any gate's tests cannot be made to pass → return to Pilot
- Scope expands to require touching gold_defaults.toml or changing JSON schemas → return to Pilot
- Gate 6 run produces zero usable events for any module → return to Pilot before proceeding

## Final Completion Criteria

- [ ] All 6 gates closed
- [ ] Each code gate completed implementer + reviewer Crew cycle
- [ ] Gate 6 report reviewed and metrics plausible
- [ ] Evidence satisfies close criteria for every gate
- [ ] Assumptions still hold (2018–2024/2025 split unchanged, #270 still deferred)
- [ ] Architecture reconciliation checked (new features + holdout modes documented)
- [ ] Triage candidates routed (#211 to issue, #270 stays open)
- [ ] Workbench artifacts archived
