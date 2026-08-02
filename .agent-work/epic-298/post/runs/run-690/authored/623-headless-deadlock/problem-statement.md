# #623 — Problem statement (understand step)

## Ask (reconciled against LAUNCH_ORDER Mission + pre-diagnosis)

`backtest_sampled_runtime` / `sampled_runtime_from_manifest` + score deadlocks at 0% CPU on
race 1 in any headless/no-console context (background task, `Start-Process -WindowStyle
Hidden`, fully detached). Works only in a real interactive terminal. Blocks every automated
evo A/B and headless gold-cycle (epic #601 Phase 0 prerequisite).

## Baseline verification against actual code (map-first reconciliation)

The launch order's pasted pre-diagnosis (`.agent-work/601-stage1-pregrease/x623-diagnosis.md`)
claims the root cause is the first real PyTorch forward pass
(`src/evo_predictor/module_runtime.py:~194`) — torch's native CPU thread pool initializes
lazily on first big batched op, and that init is console-handle-dependent on Windows.

Verified directly against the worktree code (fix/623-headless-deadlock @ c62a6430):
- `src/evo_predictor/module_runtime.py:194` is exactly
  `prediction = loaded.module.predict(pair_batch.batch)` — confirmed line match, not a stale
  reference.
- `src/evo_predictor/run.py` does NOT import torch at all today (grep confirms zero `torch`
  hits in the file); its own import block (lines 19-65) transitively imports
  `src/latent_power/training.py` and `src/evo_predictor/latent_power_bundle.py`, both of which
  `import torch` at module level — so torch is already loaded into the process well before
  `run_module_field` executes, but its native thread pool is NOT spun up until the first real
  batched op (matches the diagnosis's "lazy init on first use" claim).
- The issue's own repro matrix (plain sequential `plan=None` also hangs) rules out
  loky/ProcessPoolExecutor as the root cause per the diagnosis's reasoning — confirmed by
  reading `sampled_backtest.py`/`sampled_backtest_scoring.py`: the parallel path is only taken
  when `plan is not None and plan.n_workers > 1`; `plan=None` goes straight to
  `_score_races_sequential`, a plain for-loop with no process pool.
- Precedent for the fix pattern already exists in this repo:
  `src/utils/utilization.py:203-220` (`init_worker`) sets
  `OMP_NUM_THREADS`/`MKL_NUM_THREADS`/`OPENBLAS_NUM_THREADS`/`NUMEXPR_NUM_THREADS` env vars and
  calls `torch.set_num_threads(threads_per_worker)`, guarded by a bare try/except since torch
  may be absent for non-training jobs — but this only runs inside `ProcessPoolExecutor`
  workers, never at the plain CLI entrypoint that the headless hang actually goes through.

Baseline confirmed accurate: this is a genuine, still-open gap (not already fixed), and the
recommended fix (cap torch to 1 thread unconditionally at the `run.py` entrypoint, before any
transitive torch import triggers native thread-pool creation) is the correct, minimal,
in-scope fix per the launch order's pre-rulings.

## Decision citation

Per LAUNCH_ORDER "Pre-Rulings" #1/#2: apply `torch.set_num_threads(1)` unconditionally at the
entrypoint (not gated on `isatty()`), plus the `OMP_NUM_THREADS`/`MKL_NUM_THREADS`/etc. env
vars as belt-and-suspenders, mirroring `src/utils/utilization.py:init_worker`'s existing
guarded-import pattern. No structural/architecture change needed — this stays a bounded fix.

user-decision: cite=LAUNCH_ORDER:Mission — Admiral-ratified mission ("a sampled backtest that
runs to completion headlessly") reconciled against verified code; proceeding under
Pre-Rulings #1/#2.
