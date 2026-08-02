# Problem Statement — Issue #356: utilization knob

**Confirmed by human:** 2026-06-03 (understand.done checkpoint)

## Goal
Add one `utilization` intensity dial (`background` / `balanced` / `max`) that trades machine
usage from "reproduce today's sequential behavior" up to "saturate the box, finish ASAP" —
**without changing results**. Orthogonal to the existing `--max-rounds-per-year` fidelity dial.

## Shared core — new `src/utils/utilization.py` (Data region; nothing F1-specific)
- `resolve_resource_plan(level, *, physical_cores=None, available_mem_gb=None, mem_per_worker_gb=1.0)`
  → `ResourcePlan(level, n_workers, threads_per_worker, priority)`. Enforces `workers × threads ≈ cores`
  with a **non-user-facing RAM auto-cap** (`mem_per_worker_gb=1.0`, logged when it binds).
- `init_worker(threads_per_worker, priority)` — module-level/picklable; sets thread env
  (OMP/MKL/OPENBLAS/NUMEXPR) + `torch.set_num_threads` + OS priority (psutil) per spawned process.
- `run_jobs(jobs, worker_fn, plan, *, on_complete=None, fail_fast=True, logger=None)` —
  `ProcessPoolExecutor`; **`n_workers == 1` short-circuits to an in-process loop** (no pool/pickling);
  results reassembled in **input order**; `fail_fast` surfaces the first error with the failing job's
  identity and tears the pool down (no deadlock).

| level | 8-core box | threads | priority |
|---|---|---|---|
| background | 1 worker | 1 | idle/below-normal |
| balanced (gold default) | 4 workers | 2 | normal |
| max | 7 workers | 1 | normal |

## Scope (one PR)
All four gold-cycle phases:
- `_train_all_modules` (12 main runs)
- `_collect_loso_fusion_train_rows` (84 LOSO runs)
- `_blocked_calibration_module_rows` (12 calibration runs)
- `_run_sampled_backtest_phase` → `backtest_sampled_runtime` (~24 races; **per-race refactor** to expose
  a pure `_score_one_race` + thin driver mapping via `run_jobs`)

Plus both standalone scripts:
- `scripts/build_rolling_compound_priors.py` (8 years × rounds)
- `scripts/run_sampled_runtime_comparison.py` (default/trained × years)

Excluded: legacy `scripts/run_full_pipeline.py` (unrelated Monte-Carlo path).

## Config / CLI
- `utilization` added to `GoldCycleRuntimeConfig`, validated against `("background","balanced","max")`;
  default `balanced` in `configs/evo/gold_defaults.toml`; wired into `_config_to_raw` + override `section_map`.
- `--utilization {background,balanced,max}` on the `gold-cycle` subparser; applied **directly post-load**
  (bypasses `apply_cli_overrides`), so it works in gold mode and never lands in `applied_overrides`.
- Each standalone script gets its own `--utilization` flag.

## Determinism (the guarantee we test)
- Byte-identical at a **fixed** `threads_per_worker` regardless of `n_workers` (input-order reassembly +
  self-seeded units: training `torch.manual_seed`, pure per-race sampled backtest, deterministic prior fits).
- Metric-identical within tolerance across thread counts (float-reduction nondeterminism).
- Canonical test: a tiny smoke gold cycle (1-worker vs N-worker byte-identity at fixed threads) +
  lighter "parallel matches sequential" smoke checks on the two scripts.

**AMENDMENT (2026-06-03, human-approved at G6):** trained-weight byte-identity is physically unattainable on this
torch 2.10 CPU / py3.14 / Windows stack — even single-thread + same-seed + fixed PYTHONHASHSEED training drifts
~3e-4 run-to-run from intrinsic FP reduction-order nondeterminism. Empirically, worker count adds NO systematic
divergence (1-vs-2-worker drift 2.8e-4 ≈ same-path rerun drift 3.1e-4), so `run_jobs` is faithful. The accepted
guarantee for #356 is therefore: **structural byte-identity** (result count, input-order job keys, manifest/backtest
JSON structure with timestamps/paths/numeric-leaves normalized, artifact filenames) **+ trained-weight agreement
within 1e-2** (30× over the noise floor), with empirical proof parallelism adds no drift. The broader
"torch CPU training isn't bit-reproducible" investigation is split into a separate issue.

## Protected intent (must not regress)
- Results never depend on how hard we push the machine; `background` reproduces today's path.
- No silent oversubscription (`workers × threads ≈ cores`; plan logged once per phase; RAM cap logged when binding).
- DB-only analysis constraint and gold-mode leakage rules untouched.
- No mutable module-level runtime state / module-level DatabaseManager singletons (review blockers per Charter).

## Evidence obligations (from Charter)
- `py -m src.utils.simplification_limits` on every touched `src/` and `tests/` path (strict).
- Focused region suites: evo unit suite + the new `tests/unit/.../test_utilization.py`; gold-cycle smoke.
- `psutil` declared as a real dependency in `pyproject.toml` (currently installed but verify declared).
