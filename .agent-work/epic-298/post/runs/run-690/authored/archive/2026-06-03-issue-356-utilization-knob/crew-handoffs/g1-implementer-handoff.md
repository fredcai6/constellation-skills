# Implementer Handoff

## Gate
g1 — Shared utilization core

## Task
Create `src/utils/utilization.py`: a generic, F1-agnostic resource-policy core that maps a
utilization level to a worker/thread/priority plan and runs a list of jobs through a process
pool (or in-process). Declare `psutil` in `pyproject.toml`. Build it test-first.

## Protected Intent
Results must never depend on how hard the machine is pushed. The pool must reassemble results in
**input order** so callers are byte-identical regardless of worker count. `n_workers == 1` must be
a plain in-process loop (no pool, no pickling) so it reproduces today's sequential path exactly.

## Test Mode
TDD required (red-green-refactor). Write `tests/unit/test_utilization.py` first, watch it fail for
the right reason, then implement to green, then refactor. This module is foundational — every later
gate depends on it.

## Close Criteria
- `UTILIZATION_LEVELS = ("background", "balanced", "max")` exported.
- `ResourcePlan` is a `@dataclass(frozen=True)` with fields `level: str, n_workers: int, threads_per_worker: int, priority: str` (priority ∈ {"idle","below_normal","normal"}).
- `resolve_resource_plan(level, *, physical_cores=None, available_mem_gb=None, mem_per_worker_gb=1.0) -> ResourcePlan`:
  - `physical_cores` defaults to `psutil.cpu_count(logical=False) or os.cpu_count() or 1`.
  - Mapping: `background → (1, 1, "below_normal")`; `balanced → (max(1, cores//2), 2, "normal")`; `max → (max(1, cores-1), 1, "normal")`.
  - RAM cap: `available_mem_gb` defaults to `psutil.virtual_memory().available / 1024**3`; cap `n_workers = min(n_workers, max(1, floor(available_mem_gb / mem_per_worker_gb)))`. When the cap LOWERS n_workers, log one `logging.getLogger(__name__).info(...)` line naming the before/after and the reason.
  - Always log the resolved plan once at info level.
  - Invalid `level` → `ValueError` naming field, expected set, and actual value.
  - Invariant: `n_workers * threads_per_worker <= cores` always holds for the returned plan.
- `init_worker(threads_per_worker, priority) -> None` — **module-level** (usable as a `ProcessPoolExecutor` initializer, so it must be importable/picklable):
  - Sets env `OMP_NUM_THREADS`, `MKL_NUM_THREADS`, `OPENBLAS_NUM_THREADS`, `NUMEXPR_NUM_THREADS` = `str(threads_per_worker)`.
  - Then `import torch; torch.set_num_threads(threads_per_worker)` **guarded** by try/except (torch may be absent for non-training jobs — must not crash).
  - Sets OS priority via psutil: Windows `IDLE_PRIORITY_CLASS` for "idle" / `BELOW_NORMAL_PRIORITY_CLASS` for "below_normal" / leave for "normal"; POSIX via `os.nice` (e.g. +10 idle, +5 below_normal). Guard with try/except (best-effort).
- `run_jobs(jobs, worker_fn, plan, *, on_complete=None, fail_fast=True, logger=None) -> list`:
  - `worker_fn` is a picklable callable `(job) -> result`; `jobs` a sequence.
  - **`plan.n_workers == 1`**: apply `init_worker(plan.threads_per_worker, plan.priority)` to the current process, then run jobs sequentially; return results in input order; call `on_complete(completed_count, total, result)` after each.
  - **otherwise**: `ProcessPoolExecutor(max_workers=plan.n_workers, initializer=init_worker, initargs=(plan.threads_per_worker, plan.priority))`; submit all, track `future -> input_index`; iterate `as_completed`; place each result at `results[input_index]`; call `on_complete(completed_count, total, result)` in completion order. **Return results in INPUT order.** Do NOT call `init_worker` on the parent process in this branch (only workers lower threads/priority).
  - `fail_fast=True`: the first worker exception is re-raised wrapped with the failing job's identity (input index + `repr(job)` truncated), after the pool is torn down (use the `with` block); no deadlock.

## Allowed Scope
- `src/utils/utilization.py` (new)
- `tests/unit/test_utilization.py` (new)
- `pyproject.toml` (add `psutil` to runtime dependencies)

## Specific Exclusions
- Do NOT touch any `gold_cycle`, `sampled_backtest`, `run.py`, or `scripts/` code — later gates.
- `utilization.py` must import cleanly **without torch installed** (torch import is lazy/guarded).
- Do NOT add any new user-facing config/CLI knob (mem_per_worker_gb stays a function default).

## Constraints
- Use `py`, not `python`.
- Nothing F1-specific in this module (no DB, no calendar, no evo imports).
- No mutable module-level runtime state; no caches of impure values.
- Library logging via `logging.getLogger(__name__)`; no `print()`.
- Validation messages name field, expectation, and actual value.
- **Windows spawn gotcha:** test helper `worker_fn`s and job payloads must be **module-level** functions/values in the test file (no lambdas/closures), or the ProcessPool tests will fail to pickle under spawn.

## Required Evidence
- The red-phase failure (tests failing for the right reason) noted, then green.
- `py -m pytest tests/unit/test_utilization.py -q` → all pass (paste tail).
- `py -m src.utils.simplification_limits --paths src/utils/utilization.py tests/unit/test_utilization.py` → clean.
- The `psutil` line added to `pyproject.toml`.
- Suggested test cases: per-level mapping at `physical_cores=8`; `cores=1` clamps to ≥1; RAM cap binds (`available_mem_gb=2, mem_per_worker_gb=1, max` → 2 workers) and logs; `physical_cores=None` fallback (monkeypatch); invalid level → ValueError; `run_jobs` input-order reassembly under multi-worker; `n_workers==1` takes in-process path (monkeypatch `ProcessPoolExecutor` to raise and confirm success); a raising job surfaces wrapped with job identity; `on_complete` called `total` times.

## Verification Commands
```bash
py -m pytest tests/unit/test_utilization.py -q
py -m src.utils.simplification_limits --paths src/utils/utilization.py tests/unit/test_utilization.py
```

## Suggested Model Tier
stronger — reason: concurrency correctness (ProcessPool, spawn, ordering, fail-fast) and the determinism contract that every later gate relies on.

## Authority
Decided (do not re-litigate): the public API shape above, the three levels and their mappings,
the in-process short-circuit at 1 worker, `mem_per_worker_gb=1.0` as a function default, the
priority names. You may choose internal helper structure and exact test design. You may NOT change
the public API, add F1 specifics, or introduce new user-facing knobs.

## Stop Conditions
Stop and return if: allowed scope must be exceeded, a specific exclusion must be touched, required
evidence cannot be produced, or a decision outside the given authority is needed.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence produced
(command output tails), assumptions used, stop conditions hit, out-of-scope observations.
