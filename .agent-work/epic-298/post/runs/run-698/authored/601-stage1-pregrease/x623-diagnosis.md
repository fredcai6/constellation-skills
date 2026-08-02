# #623 headless deadlock — pre-diagnosis

## Bottom line

**Most likely blocking call:** `src/evo_predictor/module_runtime.py:194` —
`prediction = loaded.module.predict(pair_batch.batch)`, the **first real PyTorch
forward pass in the process's lifetime** (torch 2.10.0+cpu, built with
`USE_PTHREADPOOL` + Intel MKL/OpenMP per `torch.__config__.show()`). PyTorch's
native CPU thread pool initializes **lazily on first use**, gated by ATen's
`parallel_for` grain-size threshold — small tensor ops (state_dict copies during
model load) stay single-threaded and never touch the pool, but the first full
batched forward pass over a race's field of drivers is big enough to trigger it.
That first call happens inside `_score_one_race`'s quali stage for race 1, which
is exactly where the hang is observed (log line "race 1/N" already printed, then
CPU=0). **Recommended fix:** call `torch.set_num_threads(1)` (and
`torch.set_num_interop_threads(1)` if not already parallel-region-locked) at the
very top of the backtest entrypoint — before `sampled_runtime_from_manifest` is
even called — in `src/evo_predictor/run.py`, right after `import torch`. Per-race
per-driver batches here are tiny (order ~20 drivers); intra-op parallelism buys
nothing, so forcing single-threaded execution removes the thread-pool spin-up
path entirely rather than trying to time-guard it.

## Why the loky/joblib hypothesis in the issue doesn't hold up

The issue's own repro matrix says **plain sequential (`plan=None`) also hangs**,
not just the parallel `ResourcePlan` pool. That's the key fact that rules out
`ProcessPoolExecutor`/loky/joblib as the *root* cause:

- `backtest_sampled_runtime` (`src/evo_predictor/sampled_backtest.py:492-523`)
  only takes the `ProcessPoolExecutor` path (`_score_races_parallel`,
  `sampled_backtest_scoring.py:356-393`, which calls `run_jobs` →
  `src/utils/utilization.py:294-321`) when `plan is not None and plan.n_workers > 1`.
  With `plan=None` it goes straight to `_score_races_sequential`
  (`sampled_backtest_scoring.py:317-353`), a plain Python `for` loop with **no
  process pool, no `multiprocessing`, no `joblib`/`loky` anywhere in the call
  chain**. I grepped the whole predict path
  (`sampled_backtest.py`, `sampled_backtest_scoring.py`, `sampled_runtime.py`,
  `module_runtime.py`, `latent_power_bundle.py`) for `joblib`, `loky`,
  `multiprocessing`, `DataLoader`, `num_workers=` — none appear. The only
  `ProcessPoolExecutor` use in this repo's backtest surface is stdlib
  `concurrent.futures` in `src/utils/utilization.py:24,267`, and it's only
  reachable via the `n_workers > 1` branch.
- Also worth noting: even for the *parallel* branch, this codebase uses stdlib
  `concurrent.futures.ProcessPoolExecutor`, not literal `loky`. Windows'
  `multiprocessing.resource_tracker` (the thing "loky resource_tracker" usually
  refers to) is a POSIX-semaphore-tracking helper that stdlib
  `ProcessPoolExecutor` doesn't spin up on Windows for plain pipe-based IPC (no
  `shared_memory`/`sem_open` primitives are used here). So even if the parallel
  path has its own separate headless issue, "loky resource_tracker" is very
  unlikely to be its mechanism either.
- Since the hang reproduces identically whether or not a process pool is even
  in the picture, the common factor has to be something both paths share:
  DB reads via `DatabaseManager`/sqlite, feature building
  (`build_sampled_runtime_features`), and — the one substantial the-first-time-
  it-happens-in-the-process event — the first PyTorch forward pass.

## Other candidates checked and ruled out

- **tqdm-on-no-tty:** grepped the whole repo; `tqdm` is not imported anywhere
  under `src/` (only appears in `.pyc` caches from unrelated modules like
  `gold_cycle/parallel_jobs.py`, not the backtest path). Ruled out.
- **stdin/console reads (`input()`, `click.confirm`, `msvcrt`):** none in the
  predict/backtest call chain. The only `input(` hits were false positives —
  substrings of `_validate_solver_input` / `_validate_tire_wear_input` in
  `src/compound_prior/solver/_core.py` and `_iterate.py` (unrelated validation
  functions, not stdin reads), and that solver isn't even on this call path.
- **sqlite lock contention:** `DatabaseManager` reads
  (`get_session_classification`, `get_race_start_order`) run before `predict()`
  is called for each race; nothing here holds a long-lived write lock, and nothing
  in the repro (single process, no concurrent writer) would explain a first-race
  block. Lower-probability than the torch thread-pool path but not fully
  excludable from static reading alone — see verification note below.
- **A quick headless smoke test in this sandboxed Bash shell (`py -c
  "import torch; (torch.randn(2000,2000) @ torch.randn(2000,2000)).sum()"`)
  completed fine (~0.9s) with no `KMP_DUPLICATE_LIB_OK` or other
  OMP/MKL env vars set.** This doesn't rule out the thread-pool theory — this
  shell still has *some* console/pty behind it (Git Bash), which is a different
  headlessness regime than the fully `DETACHED_PROCESS` / no-window-station
  launches described in #623 (`Start-Process -WindowStyle Hidden`, OS-detached).
  The issue's own signature — "the only thing that worked was a foreground
  command that got auto-backgrounded *after* starting" — is the classic
  signature of a resource that must be acquired **at process/console-creation
  time**; once acquired it's fine even if the console goes away later. That
  points at a console-handle-dependent init path, which is consistent with
  Windows PyTorch/MKL thread-pool creation but not with a generic "can't read
  stdin" style block. It could not be fully confirmed without reproducing
  inside the exact `DETACHED_PROCESS`/no-window-station launch used in #601 —
  flagging that as the one open item for whoever picks this up (repro with
  `torch.set_num_threads(1)` set *before* import in a truly detached launch
  would confirm/deny in ~1 race).

## Recommended fix, concretely

In `src/evo_predictor/run.py`, at the top of the module (immediately after
`import torch`, before any CLI command — `sampled-predict` / `backtest` /
`gold-cycle` all import this module) add:

```python
import torch
torch.set_num_threads(1)
```

This forces PyTorch to skip lazy native thread-pool creation altogether (single
thread never needs the pool), removing the console-handle-dependent init path
from the hot loop regardless of *why* it hangs headless — it's the cheapest,
most targeted version of the issue's Option 1 ("loky-free... path usable
headless") applied to the actual parallel primitive in play (torch's own
intra-op thread pool, not loky). Given per-race batches are ~20 drivers, the
serialization cost is negligible relative to the 219s/race runtime already
observed. If a Commander wants belt-and-suspenders, also set
`OMP_NUM_THREADS=1` / `MKL_NUM_THREADS=1` env vars before the `import torch` line
(covers the MKL/OpenMP layer directly, same spirit as
`src/utils/utilization.py:213-214`'s `init_worker`, but applied unconditionally
at entrypoint rather than only inside pool workers).
