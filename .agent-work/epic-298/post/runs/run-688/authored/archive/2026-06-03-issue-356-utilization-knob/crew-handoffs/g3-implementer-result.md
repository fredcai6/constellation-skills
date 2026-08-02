# IMPLEMENTER_RESULT — g3 (parallelize the three training loops)

Status: complete. TDD red->green. No numeric/output change; only dispatch mechanism.

## Files changed
- `src/evo_predictor/gold_cycle/parallel_jobs.py` (NEW) — frozen picklable `TrainBacktestJob`
  (train Namespace, backtest_templates tuple WITHOUT bundle, key) + module-level `run_train_backtest(job)`
  (lazy-imports cmd_train/cmd_backtest; trains; stamps bundle=manifest on each template; runs backtests;
  returns {key, manifest_path, backtest_outputs}). Picklable primitives/paths only.
- `src/evo_predictor/gold_cycle/runner.py` — resolve plan once (resolve_resource_plan(...), self-logs),
  thread into 3 phases; `_train_all_modules` builds jobs via build_main_train_backtest_jobs, run_jobs +
  on_complete ETA, input-order assembly; extracted `_finalize_and_write_reports` + `_make_eta_on_complete`.
- `src/evo_predictor/gold_cycle/runner_support.py` — `_collect_loso_fusion_train_rows` +
  `_blocked_calibration_module_rows` accept plan, pre-create dirs, build jobs in SAME nested order
  (shared _iter_loso_units), run_jobs, input-order assembly; builders build_loso_train_backtest_jobs /
  build_calibration_train_backtest_jobs; extracted _parse_loso_event_rows (parsing unchanged).
- `tests/unit/evo_predictor/test_gold_cycle_parallel_jobs.py` (NEW, 7 tests) — frozen+picklable, worker
  train->stamp->backtest, three builders' order/args, non-spawning guard (patch ProcessPoolExecutor to raise).
- `tests/unit/evo_predictor/test_gold_cycle_runner.py` — pass background plan to _collect_loso_fusion_train_rows.

## Test mode: TDD satisfied
- RED: parallel_jobs tests failed with ModuleNotFoundError / ImportError (feature absent).
- GREEN: all pass. Corrected one guessed calibration expectation to the real calibration_fit_split contract.
- Refactor while green: helper extraction; tests stayed green.

## Evidence
- `py -m pytest tests/unit/evo_predictor/test_gold_cycle_runner.py tests/unit/evo_predictor/test_gold_fusion_train_rows.py -q` -> 33 passed (40 incl. new file; 83 adjacent suites).
- `--paths parallel_jobs.py runner.py runner_support.py` -> FAIL (2 violations) BOTH on _gold_preflight_coverage
  (CC=21, lines=114) which is PRE-EXISTING and UNTOUCHED. parallel_jobs.py PASS, runner.py PASS.
  NO NEW violations. _collect_loso_fusion_train_rows refactor brought it UNDER limits (was CC=20/135).
- Non-spawning: tests run at utilization=background (in-process); guard test confirms ProcessPoolExecutor never constructed.

## Behavior-preservation note (for reviewer)
- Calibration: implementer states calibration_fit_split yields a SINGLE prediction year (train_years[-1]),
  so each calibration job carries exactly one backtest template, matching the original `for prediction_year in
  fit_prediction_years` loop. REVIEWER MUST CONFIRM this equivalence (that fit_prediction_years is length 1, or
  that all prediction years are carried as templates) to guarantee byte-identity.
- _finalize_and_write_reports extraction must preserve report assembly exactly.

## Exclusions respected
- _run_sampled_backtest_phase / backtest_sampled_runtime (G4), scripts (G5), report schema/run_config: untouched.

## Out-of-scope observations
- _gold_preflight_coverage (runner_support.py) remains over limits (CC=21, lines=114) — pre-existing; belongs
  with tc1 decomposition follow-up.
