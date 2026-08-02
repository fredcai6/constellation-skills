# Reviewer Handoff

## Gate
g3 — Parallelize the three gold-cycle training loops

## What Was Implemented
New `gold_cycle/parallel_jobs.py` (frozen picklable TrainBacktestJob + module-level run_train_backtest worker);
`run_cycle` resolves a utilization plan once and threads it into the three loops; `_train_all_modules`,
`_collect_loso_fusion_train_rows`, `_blocked_calibration_module_rows` now build jobs and fan out via `run_jobs`
with input-order assembly. New parallel_jobs test file; runner test updated to pass a background plan.

## How to Inspect the Diff
- `git diff -- src/evo_predictor/gold_cycle/parallel_jobs.py src/evo_predictor/gold_cycle/runner.py src/evo_predictor/gold_cycle/runner_support.py tests/unit/evo_predictor/test_gold_cycle_runner.py tests/unit/evo_predictor/test_gold_cycle_parallel_jobs.py`
- `git status --porcelain` to confirm only those files changed (ignore `.agent-work/`).
Note parallel_jobs.py + parallel test file are new/untracked — read them directly.
Implementer result: `.agent-work/issue-356-utilization-knob/crew-handoffs/g3-implementer-result.md`.

## Task Statement
Convert the three sequential train+backtest loops to fan out through run_jobs, driven by the resolved
utilization plan, with byte-identical output (same args, same order, input-ordered assembly) and the
background (1-worker) path reproducing today's behavior. Full handoff:
`.agent-work/issue-356-utilization-knob/crew-handoffs/g3-implementer-handoff.md`.

## Close Criteria (each a review check)
- **Byte-identity by construction:** each loop builds its job list in the SAME order and with the SAME args as
  the prior nested iteration; outputs (module_manifests dict / all_rows list / calibration_rows list) are
  assembled by iterating results in INPUT order. Read the builders and confirm order/args match the originals.
- **CALIBRATION EQUIVALENCE (scrutinize):** the original `_blocked_calibration_module_rows` looped
  `for prediction_year in fit_prediction_years` and emitted one row per prediction year. The new code collapses
  to one backtest template per module. CONFIRM this is equivalent — i.e. that `calibration_fit_split` truly
  yields exactly ONE fit_prediction_year (so one row per module), OR that the job carries ALL prediction years
  as templates and emits all rows. If fit_prediction_years can be length>1 and only one is carried, that's a
  BLOCK (silent output change).
- **Report assembly unchanged:** the extracted `_finalize_and_write_reports` must produce the same reports as
  before (no reordering/dropping of report fields).
- Worker fns module-level; jobs carry only picklable primitives/paths (no DB handles, no tensors).
- background (1 worker) takes the in-process path (no ProcessPoolExecutor constructed) — confirm via the guard test.
- Progress logging coherent under concurrency (on_complete completed-count + wall-clock ETA); final summary line preserved.

## Allowed Scope
parallel_jobs.py (new), runner.py, runner_support.py, the two named test files.

## Specific Exclusions (flag if touched)
No `_run_sampled_backtest_phase` / `backtest_sampled_runtime` change (G4). No scripts (G5). No report-schema /
run_config change. No change to training/backtest numerics or arg VALUES (only dispatch).

## Constraints the Implementation Must Respect (each a review check)
- Determinism: input-order assembly everywhere.
- DB-only; logging not print; module-level spawn-safe workers.
- **Simplification standard (Commander-set):** bar is NO NEW violation. Re-run `--paths` and confirm: parallel_jobs.py
  and runner.py pass; the only failure is the PRE-EXISTING, UNTOUCHED `_gold_preflight_coverage` (CC=21/114). Confirm
  the implementer's claim that `_collect_loso_fusion_train_rows` is now UNDER limits (improved). Do NOT block on the
  pre-existing `_gold_preflight_coverage`. BLOCK if any NEW violation was introduced.

## Evidence Produced
- `py -m pytest tests/unit/evo_predictor/test_gold_cycle_runner.py tests/unit/evo_predictor/test_gold_fusion_train_rows.py -q` → 33 passed (re-run; also run the new test_gold_cycle_parallel_jobs.py).
- Re-run `--paths` and classify failures (expect only pre-existing _gold_preflight_coverage).

## Suggested Model Tier
stronger — reason: behavior-preservation under refactor + concurrency; the calibration-equivalence and
order/args checks are subtle and a mistake silently changes gold outputs.

## Stop Conditions
Return BLOCK if: job order/args diverge from the originals, calibration emits a different row set, report assembly
changes, a NEW simplification violation appears, an exclusion was touched, or jobs carry non-picklable data.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings, blockers (file:line + issue), out-of-scope observations.
