# Implementer Handoff

## Gate
g4 — Sampled-backtest per-race refactor + parallelization

## Task
Extract the per-race body of `backtest_sampled_runtime` (`src/evo_predictor/sampled_backtest.py`) into a pure
`_score_one_race(...)` helper, make the function a thin driver that maps races (sequentially in-process by default,
or via `run_jobs` when a multi-worker plan + reconstruction paths are supplied), and wire the plan in from
`_run_sampled_backtest_phase`. Behavior must be byte-identical to today.

## Protected Intent
`backtest_sampled_runtime` is called by tests, the CLI (`cmd_sampled_backtest`), and the gold cycle. Its default
behavior MUST be unchanged: default to in-process sequential scoring producing the exact same per_race order,
skipped list, diagnostics, and aggregate. Parallelism is OPT-IN (plan + paths) and must yield identical results.

## Test Mode
TDD for a behavior-preserving refactor: FIRST confirm the existing sampled-backtest suite is green (your
characterization baseline); add characterization tests for any uncovered skip path BEFORE refactoring; refactor;
keep green. The multi-worker byte-identity is finalized in G6 — but add a focused equivalence test here if a
fixture makes it cheap.

## The per-race loop today (lines ~474-618)
Each race iteration produces EITHER a scored `SampledBacktestRaceResult` appended to `per_race`, OR a skip dict
appended to `skipped`, via these steps: actual_results lookup (skip if missing) → quali/race_start truth →
oracle_state (skip on OracleStateUnavailableError) → `runtime.predict(...)` → `_compute_entrant_restriction`
(skip on missing entrants) → `sampled_order_metrics` (skip on ScoringContractError / ValueError) → per-stage
metrics → append SampledBacktestRaceResult. The final diagnostics/aggregate assembly stays in the driver.

## Close Criteria
- `_score_one_race(runtime, *, year, round_num, gp_name, db, compound_normalizer, mode) -> <tagged outcome>` is a
  PURE function containing exactly the per-race body. Returns a tagged outcome distinguishing scored (carrying the
  `SampledBacktestRaceResult`) vs skipped (carrying the skip dict) — e.g. a small frozen dataclass or a
  `(result|None, skip|None)` pair. No shared mutable state; no module-level globals.
- `backtest_sampled_runtime` gains OPTIONAL params: `plan=None` and reconstruction paths
  `manifest_path=None, db_path=None, compound_prior_root=None`.
  - **Default / `plan is None` or `plan.n_workers == 1`:** sequential in-process — for each selected race call
    `_score_one_race` with the LIVE `runtime`/`db`/`compound_normalizer`; partition into per_race/skipped in
    calendar (input) order. (This is the pure refactor — the main behavior-preservation proof.)
  - **`plan.n_workers > 1` WITH reconstruction paths:** build one job per race carrying
    `(manifest_path, db_path, compound_prior_root, year, round_num, gp_name, mode, target_lap)`; run via
    `run_jobs(jobs, _score_one_race_job, plan, on_complete=...)`; partition results in INPUT order.
  - **`plan.n_workers > 1` WITHOUT the paths:** raise a clear `ValueError` naming what's missing (do NOT silently
    fall back — fail fast). Only `_run_sampled_backtest_phase` sets a multi-worker plan and it WILL pass paths.
- Module-level `_score_one_race_job(job)` worker: rebuild `runtime = sampled_runtime_from_manifest(manifest_path)`,
  `db = DatabaseManager(db_path=db_path)`, and `compound_normalizer` from `load_time_safe_compound_prior(
  compound_prior_root, target_year=year)` → `CompoundNormalizer(artifact)` (mirror how `_run_sampled_backtest_phase`
  / `_run_evidence_mode_eval` build them); then call `_score_one_race`. Only picklable primitives/paths in the job.
- `run_cycle` passes the already-resolved `plan` (from G3) into `_run_sampled_backtest_phase`, which passes
  `plan` + `manifest_path=sampled_manifest` + `db_path` + `compound_prior_root` into `backtest_sampled_runtime`.

## Allowed Scope
- `src/evo_predictor/sampled_backtest.py` (extract helper + driver + worker)
- `src/evo_predictor/gold_cycle/runner.py` (`_run_sampled_backtest_phase` signature + pass plan/paths; run_cycle call site)
- `tests/unit/evo_predictor/test_sampled_backtest.py`, `tests/unit/evo_predictor/test_sampled_backtest_cli.py`

## Specific Exclusions
- Do NOT change the training loops (G3, done) or the standalone scripts (G5).
- Do NOT change scoring numerics, skip semantics, diagnostics keys, or aggregate computation — only HOW races are iterated.
- Do NOT add a module-level mutable cache of runtime/db (review blocker). Rebuilding per job is acceptable
  (correctness first; a worker-local cache is a possible FUTURE perf follow-up — note it, don't build it).
- Do NOT add `utilization` to the report schema.

## Constraints
- Use `py`, not `python`.
- Determinism: partition per_race/skipped in INPUT (calendar) order; run_jobs returns input-ordered results.
- `_score_one_race` pure; worker module-level + spawn-safe; jobs carry only picklable data.
- DB-only; logging via `logging.getLogger(__name__)`; no print().
- **Simplification standard (Commander-set):** NO NEW violation (no new file>1000 / function>100 / CC>20). The
  extracted `_score_one_race` is large — keep it < 100 lines / CC < 20 (split into sub-helpers if needed). Classify
  any `--paths` failure as pre-existing or new; NEW must be fixed.

## Required Evidence
- Baseline green BEFORE refactor (characterization), then green AFTER.
- `py -m pytest tests/unit/evo_predictor/test_sampled_backtest.py tests/unit/evo_predictor/test_sampled_backtest_cli.py -q` → pass (tail).
- `py -m src.utils.simplification_limits --paths src/evo_predictor/sampled_backtest.py src/evo_predictor/gold_cycle/runner.py <test files>` → classify pre-existing vs new.
- If feasible with fixtures: a test showing the multi-worker path yields the same per_race/skipped as in-process.

## Verification Commands
```bash
py -m pytest tests/unit/evo_predictor/test_sampled_backtest.py tests/unit/evo_predictor/test_sampled_backtest_cli.py -q
py -m src.utils.simplification_limits --paths src/evo_predictor/sampled_backtest.py src/evo_predictor/gold_cycle/runner.py
```

## Suggested Model Tier
stronger — reason: behavior-preserving extraction of a long, branch-heavy loop plus a reconstruct-from-paths worker;
a subtle change to skip semantics or ordering silently corrupts gold backtest output.

## Authority
Decided (do not re-litigate): default-in-process / opt-in-parallel contract; fail-fast (not silent fallback) when a
multi-worker plan lacks paths; worker rebuilds from paths (no module-level cache); no numeric/skip/diagnostics
change; the simplification standard. You may choose the tagged-outcome representation and sub-helper structure.

## Stop Conditions
Stop and return if: scope must be exceeded, scoring/skip/diagnostics semantics would change, a NEW simplification
violation is unavoidable without a larger refactor, evidence cannot be produced, or a decision outside authority is needed.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied (baseline-then-refactor green),
evidence (command tails; pre-existing vs new simplification), assumptions, stop conditions hit, out-of-scope observations.
