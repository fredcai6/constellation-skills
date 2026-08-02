# Implementer Handoff

## Gate
g3 — Parallelize the three gold-cycle training loops

## Task
Introduce `src/evo_predictor/gold_cycle/parallel_jobs.py` (picklable job + module-level worker) and convert
the three sequential train+backtest loops to fan out through `run_jobs` from `src.utils.utilization`, driven by
the resolved utilization plan. Results must be byte-identical to today's sequential output.

## Protected Intent
Output must not depend on worker count. Build the SAME args in the SAME order as today and assemble all results
in INPUT order. At `background` (1 worker) the in-process path must reproduce today's behavior exactly.

## Test Mode
TDD required (red-green-refactor). Existing gold-cycle tests are the safety net; add a focused test that the
loops build jobs in the same order/args as before. Keep unit tests fast (see Constraints: pin background).

## The three loops (in `runner.py` / `runner_support.py`)
1. `runner.py::_train_all_modules` — 1 train + 1 backtest per module (12). Backtest: year=eval_year,
   output=backtests_dir/{module}.json, includes retro_root.
2. `runner_support.py::_collect_loso_fusion_train_rows` — for each (fold heldout_year, module): 1 train + 1
   backtest (year=heldout_year, output=fold_backtests_dir/{module}.json). Nested order today: fold outer, module
   inner. After backtest, parse per_event into row dicts (KEEP that parsing in the parent).
3. `runner_support.py::_blocked_calibration_module_rows` — per module: 1 train, then a backtest for EACH
   fit_prediction_year (so 1 train + N backtests). Parent builds a module_report_row per (module, prediction_year).

## Close Criteria
- New `src/evo_predictor/gold_cycle/parallel_jobs.py`:
  - A frozen, picklable job dataclass carrying: the train `argparse.Namespace`, a list of backtest `Namespace`
    templates (each WITHOUT `bundle`, plus any per-backtest metadata needed to label output), and a string `key`
    for logging/identity.
  - Module-level `run_train_backtest(job) -> dict` worker: lazily import `cmd_train_latent_power_module` /
    `cmd_backtest_latent_power_module` from `src.evo_predictor.run`; run train; set `bundle=manifest_path` on each
    backtest Namespace; run each backtest; return `{"key", "manifest_path", "backtest_outputs": [paths...]}`.
    Only picklable primitives/paths cross the boundary — NO DB handles, NO tensors.
- `run_cycle` resolves the plan once: `plan = resolve_resource_plan(config.runtime.utilization,
  available_mem_gb=psutil.virtual_memory().available / 1024**3)`, logs it once, and threads `plan` into the three
  phase functions.
- Each loop builds its job list in the SAME order as the current nested iteration, calls
  `run_jobs(jobs, run_train_backtest, plan, on_complete=<progress>)`, then assembles outputs (module_manifests
  dict / all_rows list / calibration_rows list) by iterating results in INPUT order. Row-parsing logic is
  unchanged, just moved to consume results in order.
- Progress logging preserved in spirit: an `on_complete(done, total, result)` callback logs a per-completion line
  (`done <key> (k/N complete, ETA ~Mm)` using wall-clock) and the existing final summary line still fires.
- Pre-create per-fold/per-module output directories in the parent BEFORE dispatch (as today) so workers only
  write to distinct, already-existing paths (no collisions: mains→modules_dir/{module}, LOSO→fold_modules_dir
  per heldout year, calibration→calibration modules_dir; all distinct).

## Allowed Scope
- `src/evo_predictor/gold_cycle/parallel_jobs.py` (new)
- `src/evo_predictor/gold_cycle/runner.py`
- `src/evo_predictor/gold_cycle/runner_support.py`
- Tests: `tests/unit/evo_predictor/test_gold_cycle_runner.py`, `tests/unit/evo_predictor/test_gold_fusion_train_rows.py`
  (and a small new test for job-order if helpful).

## Specific Exclusions
- Do NOT touch the sampled backtest (`_run_sampled_backtest_phase` / `backtest_sampled_runtime`) — that is G4.
- Do NOT touch the standalone scripts — that is G5.
- Do NOT add `utilization` to the gold report schema / run_config.
- Do NOT change training/backtest numerics or args values — only HOW they are dispatched.

## Constraints
- Use `py`, not `python`.
- Worker fns module-level and spawn-safe; jobs carry only picklable primitives/paths.
- **Determinism: assemble every output in INPUT order** (run_jobs already returns input-ordered results — rely on it).
- DB-only analysis; no FastF1.
- Library logging via `logging.getLogger(__name__)`; no print().
- **Keep unit tests fast & non-spawning:** ensure the gold-cycle tests that exercise run_cycle/these loops run at
  `utilization="background"` (the in-process path), so no ProcessPool spawns during unit tests. (The background-vs-
  multi-worker byte-identity check is a separate gate, G6.)
- **Simplification standard (Commander-set, same as G2):** the bar is **no NEW simplification violation**
  (no new file>1000 / function>100 / CC>20). `parallel_jobs.py` and any NEW/edited function you author must be
  within limits. Pre-existing over-limit functions you must edit may stay over-limit (don't worsen them
  materially; extract the new logic into helpers where natural). Run `--paths` and confirm any failures are
  pre-existing; note new ones must be fixed.

## Required Evidence
- Red-then-green noted.
- `py -m pytest tests/unit/evo_predictor/test_gold_cycle_runner.py tests/unit/evo_predictor/test_gold_fusion_train_rows.py -q` → pass (tail).
- `py -m src.utils.simplification_limits --paths src/evo_predictor/gold_cycle/parallel_jobs.py src/evo_predictor/gold_cycle/runner.py src/evo_predictor/gold_cycle/runner_support.py <test files>` → state whether failures are pre-existing or new (new = must fix).
- A note/test demonstrating the job list is built in the same order as the prior nested loops.

## Verification Commands
```bash
py -m pytest tests/unit/evo_predictor/test_gold_cycle_runner.py tests/unit/evo_predictor/test_gold_fusion_train_rows.py -q
py -m src.utils.simplification_limits --paths src/evo_predictor/gold_cycle/parallel_jobs.py src/evo_predictor/gold_cycle/runner.py src/evo_predictor/gold_cycle/runner_support.py
```

## Suggested Model Tier
stronger — reason: concurrency + determinism + a new spawn-safe job contract across three loops with distinct
backtest shapes; ordering/labeling mistakes would silently change outputs.

## Authority
Decided (do not re-litigate): the job/worker contract above; resolve plan once in run_cycle; input-order
assembly; background-in-process for unit tests; no schema change; the simplification standard. You may choose the
exact dataclass fields, helper structure, and on_complete logging format. You may NOT change training/backtest
numerics, arg values, or the iteration order.

## Stop Conditions
Stop and return if: allowed scope must be exceeded, an exclusion must be touched, a NEW simplification violation
is unavoidable without a larger refactor, evidence cannot be produced, or a decision outside authority is needed.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied (red observed), evidence
(command tails; pre-existing vs new simplification), assumptions, stop conditions hit, out-of-scope observations.
