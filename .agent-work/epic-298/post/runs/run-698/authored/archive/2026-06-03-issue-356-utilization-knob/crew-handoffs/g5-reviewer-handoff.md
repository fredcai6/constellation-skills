# Reviewer Handoff

## Gate
g5 — Standalone scripts adopt the utilization core

## What Was Implemented
`--utilization` added to both scripts (default balanced). build_rolling_compound_priors parallelizes its per-round
loop via run_jobs with a catch-and-return worker (preserves per-round failure collection + exit code).
run_sampled_runtime_comparison runs its default+trained backtests as 2 fail_fast jobs assembled [default, trained].
New parallel smoke tests; two existing test `_args()` helpers set utilization="background" for in-process mocking.

## How to Inspect the Diff
- `git status --porcelain` (modified: the 2 scripts + 2 existing test files; NEW: 2 parallel test files; ignore `.agent-work/`).
- `git diff -- scripts/build_rolling_compound_priors.py scripts/run_sampled_runtime_comparison.py tests/`
Implementer result: `.agent-work/issue-356-utilization-knob/crew-handoffs/g5-implementer-result.md`.

## Task Statement
Both scripts adopt run_jobs under a --utilization plan, preserving output/ordering/exit-codes and each script's
distinct failure semantics. Full handoff: `.agent-work/issue-356-utilization-knob/crew-handoffs/g5-implementer-handoff.md`.

## Close Criteria (each a review check)
- Both scripts accept `--utilization {background,balanced,max}` (default balanced), validated against UTILIZATION_LEVELS.
- build_rolling: per-round jobs in round order; worker catches internally and returns a tagged result; built/failed
  partition + summary print + exit code (1 if any failed) IDENTICAL to today. fail_fast=False.
- rt-comparison: default+trained as 2 jobs, results assembled [default, trained] in INPUT order; deltas + artifacts
  identical; fail_fast=True; manifest resolution unchanged before the parallel section; no plan threaded into
  backtest_sampled_runtime.
- background (1 worker) → in-process for both; existing tests green.
- Parallel smoke tests genuinely assert ordering + built/failed semantics.

## *** PRIMARY RISK — SPAWN SAFETY (verify rigorously) ***
The issue's explicit Windows risk: ProcessPoolExecutor uses spawn; the worker entrypoint must be importable and not
rely on parent state. These scripts run as `__main__` (`py scripts/foo.py`), the most exposed case, and G6 does NOT
cover them. The implementer's smokes MOCK heavy work in-process — the REAL multi-process spawn path is UNTESTED.
DO THIS:
1. Confirm both worker fns (`_rolling_prior_job_worker`, `_backtest_job_worker`) are MODULE-LEVEL and that all heavy/
   CLI work is under `if __name__ == "__main__"` (no import-time side effects).
2. Confirm the scripts are importable as modules (e.g. `import scripts.build_rolling_compound_priors`) so a spawned
   child can resolve the worker by qualified name.
3. ATTEMPT A REAL 2-WORKER SMOKE: import the worker via the `scripts.<module>._worker` package path (NOT __main__,
   NOT importlib-by-path) and run `run_jobs` with a 2-worker plan over trivial real jobs to prove the worker pickles
   and executes under genuine spawn. If you can make this cheap and non-flaky, ADD it as a test. If genuinely
   infeasible, state precisely why and assess the residual risk (BLOCK only if you find an actual spawn defect).

## Allowed Scope
The two scripts + their test files (2 existing modified, 2 new).

## Specific Exclusions (flag if touched)
No gold cycle / src/utils/utilization.py change. No change to script output artifacts, file names, ordering, or exit codes.

## Constraints (each a review check)
- Worker fns module-level + spawn-safe; jobs carry only picklable primitives/paths; input-order assembly.
- print() is acceptable in these CLI scripts.
- **Simplification (Commander standard):** NO NEW violation. Re-run `--paths`; confirm the only failure is the
  PRE-EXISTING `run_comparison` (~134 lines; was 135 pre-G5 — not worsened). build_rolling should be clean. Don't
  block on run_comparison (tc2). BLOCK on any new violation.

## Evidence Produced
- `py -m pytest tests/unit/compound_prior/test_build_rolling_priors.py tests/unit/evo_predictor/test_sampled_runtime_comparison_manifest_resolution.py tests/unit/evo_predictor/test_sampled_runtime_comparison_reporting.py -q` plus the 2 new parallel test files → 86 passed (re-run).
- `--paths` on the two scripts → 1 pre-existing (run_comparison).

## Suggested Model Tier
stronger — reason: the spawn-safety verification (real multi-process) is the crux and requires careful, hands-on checking.

## Stop Conditions
Return BLOCK if: a real spawn defect is found, a script's output/exit-code/ordering changed, failure semantics
diverge (build_rolling must collect, rt-comparison must propagate), a NEW simplification violation appears, or scope was exceeded.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings, blockers (file:line + issue), out-of-scope
observations. If you could not run a real spawn smoke, say so explicitly and give your residual-risk assessment.
