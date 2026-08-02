# IMPLEMENTER_RESULT — g5 (standalone scripts adopt the core)

Status: complete. TDD 16-red -> 86-green.

## Files changed
- `scripts/build_rolling_compound_priors.py` — --utilization {bg,bal,max} (default balanced); module-level
  `_rolling_prior_job_worker` (try/excepts internally, returns {round_num, ok, summary_path|error}); per-round
  loop replaced with run_jobs(fail_fast=False); built/failed partitioned in round order; summary + exit code preserved.
- `scripts/run_sampled_runtime_comparison.py` — --utilization (default balanced); module-level `_backtest_job_worker`
  (propagates); default+trained run via run_jobs([default_job, trained_job], fail_fast=True); results assembled
  [default, trained] in input order; manifest resolution unchanged before parallel section.
- `tests/.../test_sampled_runtime_comparison_manifest_resolution.py` + `test_sampled_runtime_comparison_reporting.py`
  — _args() defaults utilization="background" (mock-patch tests must run in-process).
- NEW `tests/unit/compound_prior/test_build_rolling_priors_parallel.py`, NEW
  `tests/unit/evo_predictor/test_sampled_runtime_comparison_parallel.py` — parallel smoke (mocked heavy work).

## Test mode: TDD satisfied
- RED: 16 failing (missing workers, unrecognized --utilization). GREEN: 86 passed. Refactored run_comparison
  parallel block to 1 line shorter than original.

## Evidence
- `py -m pytest <3 existing + 2 new test files> -q` -> 86 passed.
- `--paths scripts/build_rolling_compound_priors.py scripts/run_sampled_runtime_comparison.py` -> 1 violation,
  `run_comparison: function_lines=134` PRE-EXISTING (was 135; now 1 shorter). No new violations. build_rolling clean.

## KNOWN GAP (Commander flagged for reviewer)
- The REAL multi-process spawn path for the scripts is NOT directly tested: smokes mock heavy work in-process
  because tests load scripts via importlib and the module isn't registered under its spawn-resolvable name.
  Scripts run as __main__ (py scripts/foo.py) -> Windows spawn + __main__ is the issue's explicit risk. Reviewer
  to attempt a REAL 2-worker smoke via the importable `scripts.<module>._worker` path, or quantify residual risk.

## Assumptions
- Existing mock-patch tests must run at background (in-process) since monkeypatch can't cross process boundaries;
  CLI default stays "balanced". Worker fns are module-level with __main__ guards (spawn-safe in principle).

## Out-of-scope observations
- run_comparison (run_sampled_runtime_comparison.py) pre-existing over 100-line limit (134) -> triage candidate.
