# REVIEW_RESULT — g5 (standalone scripts adopt the core)

Verdict: **APPROVE**

## Real multi-process spawn smoke: YES, RAN IT
- Executed a genuine 2-worker ProcessPoolExecutor (Windows spawn) over the REAL module-level workers resolved by
  `scripts.<module>._worker` qualified names (not __main__, not importlib-by-path). Both pickled + executed in
  spawned children with NO defect. Promoted to a guarded permanent regression: TestRealSpawnSmoke (~3.7s, green 3x)
  in tests/unit/compound_prior/test_build_rolling_priors_parallel.py.
  - brc worker: ran in-child, caught RuntimeError, returned tagged {ok:False}.
  - rt worker: ran in-child, propagated as JobExecutionError under fail_fast=True.

## Independent verification
- Both scripts: --utilization {bg,bal,max} default balanced, validated (choices=UTILIZATION_LEVELS); invalid -> non-zero SystemExit.
- build_rolling: per-round jobs in round order; worker catches internally, returns tagged result; built/failed +
  summary + exit code (1 if any failed) identical; fail_fast=False.
- rt-comparison: default+trained as 2 jobs assembled [default, trained] input order; deltas/artifacts identical;
  fail_fast=True; manifest resolution unchanged before parallel section; no plan threaded into backtest_sampled_runtime.
- Workers module-level (brc:158, rsrc:341); heavy/CLI under __main__; scripts import as scripts.<module> (Py3.14 namespace pkg).
- Input-order verified via spawn probe (submitted (3,1) -> [3,1]). Jobs picklable (proven via real spawn).
- 86 passed over the named files (87 with the added spawn regression). Exclusions untouched.
- Simplification: only run_comparison=134 (PRE-EXISTING; HEAD was 135 -> reduced by 1, not worsened); build_rolling clean. No new violation.

## Blockers
None.

## Out-of-scope / notes
- tc2: run_comparison 134 lines pre-existing -> extraction follow-up (do not block).
- Cosmetic: build_rolling per-round progress line now prints in on_complete (after each job); identical stdout in
  background, interleaved under multi-worker; summary/exit-code/JSON artifacts unchanged. Not a blocker.
- Reviewer added TestRealSpawnSmoke (permanent) + removed scratch probes.
