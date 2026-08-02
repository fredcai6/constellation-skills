# Implementer Handoff

## Gate
g5 — Standalone scripts adopt the utilization core

## Task
Add `--utilization` to both standalone scripts and fan their independent units out through `run_jobs` from
`src.utils.utilization`, preserving each script's existing output, ordering, and failure semantics.

## Protected Intent
Each script's results, output files, ordering, and EXIT CODE must be unchanged at `background` (1 worker,
in-process). The two scripts have DIFFERENT failure semantics — preserve each exactly (see below).

## Test Mode
TDD. Existing script tests are the safety net (keep green); add a focused "parallel matches sequential" smoke per
script (mock the heavy per-unit work so the test is fast and needs no real pool/compute).

## Script 1: `scripts/build_rolling_compound_priors.py`
- Today: `for round_num in rounds: build_rolling_prior_for_round(...)` (lines ~210-226), catching exceptions
  PER ROUND into `failed`, continuing, printing a summary, returning 1 if any failed.
- Convert to: add `--utilization {background,balanced,max}` (default "balanced"); resolve a plan; build one job
  per round (in round order); run via `run_jobs`.
- **FAILURE SEMANTICS (critical):** this script collects per-round failures and continues. `run_jobs(fail_fast=...)`
  raises on worker error — so the worker MUST be a module-level wrapper that try/excepts internally and returns a
  tagged result `{round_num, ok: bool, summary_path|error}`. run_jobs then never sees an exception; partition
  built/failed from the input-ordered results; preserve the summary print and the return code (1 if any failed).
- `build_rolling_prior_for_round` is already module-level (spawn-safe). The wrapper worker must also be module-level.

## Script 2: `scripts/run_sampled_runtime_comparison.py`
- Today: `run_comparison` runs `_run_backtest(default_manifest...)` then `_run_backtest(trained_manifest...)`
  (lines ~388-401) — two INDEPENDENT backtests to distinct output files, then computes `_metric_deltas(default, trained)`.
- Convert to: add `--utilization {background,balanced,max}` (default "balanced"); resolve a plan; run the two
  backtests as 2 jobs via `run_jobs` (a module-level worker that runs one `_run_backtest` and returns its payload);
  assemble results in INPUT order `[default, trained]` and feed `_metric_deltas` exactly as today.
- **FAILURE SEMANTICS:** the original does NOT catch around `_run_backtest`, so a backtest failure propagates and
  aborts. Use `run_jobs(fail_fast=True)` here (propagate). Manifest resolution (which raises ManifestResolutionError)
  stays BEFORE the parallel section, unchanged.
- Each worker's `cmd_sampled_backtest` runs `backtest_sampled_runtime` WITHOUT a plan → in-process (no nested pool).

## Close Criteria
- Both scripts gain `--utilization {background,balanced,max}` (default "balanced"), validated (reuse UTILIZATION_LEVELS).
- build_rolling: per-round jobs via run_jobs with a module-level catch-and-return worker; built/failed partitioned
  in round order; summary print + exit code identical to today.
- rt-comparison: default+trained via run_jobs (fail_fast=True), results assembled `[default, trained]`; deltas + all
  output artifacts identical to today.
- background (1 worker) → in-process for both (no spawn); existing script tests stay green.
- A "parallel matches sequential" smoke per script (mock heavy work; assert same built/failed and same
  default/trained payload order under a forced multi-worker plan vs background).

## Allowed Scope
- `scripts/build_rolling_compound_priors.py`
- `scripts/run_sampled_runtime_comparison.py`
- `tests/unit/compound_prior/test_build_rolling_priors.py`
- `tests/unit/evo_predictor/test_sampled_runtime_comparison_manifest_resolution.py` and/or
  `tests/unit/evo_predictor/test_sampled_runtime_comparison_reporting.py` (and/or a new focused parallel test file).

## Specific Exclusions
- Do NOT touch the gold cycle (G1-G4) or `src/utils/utilization.py`.
- Do NOT change each script's output artifacts, file names, ordering, or exit codes.
- Do NOT thread a plan into `backtest_sampled_runtime` from the rt-comparison worker (it runs in-process per worker).

## Constraints
- Use `py`, not `python`.
- Worker fns MODULE-LEVEL and spawn-safe; all heavy/CLI work stays under `if __name__ == "__main__"`; jobs carry
  only picklable primitives/paths.
- Determinism: assemble results in INPUT order (run_jobs guarantees it).
- `print()` is fine in these scripts (CLI scripts); library code still uses logging.
- **Simplification standard (Commander-set):** NO NEW violation (no new file>1000 / function>100 / CC>20). Classify
  any `--paths` failure as pre-existing vs new; NEW must be fixed.

## Required Evidence
- Red-then-green for new tests; existing green.
- `py -m pytest tests/unit/compound_prior/test_build_rolling_priors.py tests/unit/evo_predictor/test_sampled_runtime_comparison_manifest_resolution.py tests/unit/evo_predictor/test_sampled_runtime_comparison_reporting.py -q` → pass (tail), plus any new test file.
- `py -m src.utils.simplification_limits --paths scripts/build_rolling_compound_priors.py scripts/run_sampled_runtime_comparison.py <test files>` → classify pre-existing vs new.

## Verification Commands
```bash
py -m pytest tests/unit/compound_prior/test_build_rolling_priors.py tests/unit/evo_predictor/test_sampled_runtime_comparison_manifest_resolution.py tests/unit/evo_predictor/test_sampled_runtime_comparison_reporting.py -q
py -m src.utils.simplification_limits --paths scripts/build_rolling_compound_priors.py scripts/run_sampled_runtime_comparison.py
```

## Suggested Model Tier
simple bounded — well-specified; the only subtleties are the per-script failure semantics (catch-and-return vs
fail-fast) and spawn-safety of the worker fns.

## Authority
Decided (do not re-litigate): default "balanced" for both scripts; build_rolling uses a catch-and-return worker to
preserve failure collection; rt-comparison uses fail_fast=True; no nested plan into backtest_sampled_runtime; no
output/exit-code change; the simplification standard. You may choose worker/job shape and test structure.

## Stop Conditions
Stop and return if: scope must be exceeded, a script's output/exit-code/ordering would change, a NEW simplification
violation is unavoidable, evidence cannot be produced, or a decision outside authority is needed.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied (red observed), evidence (command
tails; pre-existing vs new simplification), assumptions, stop conditions hit, out-of-scope observations.
