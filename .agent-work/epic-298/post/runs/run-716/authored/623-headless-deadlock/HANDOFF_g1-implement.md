# Implementer Handoff

## Gate
g1-implement (work-id 623-headless-deadlock, branch fix/623-headless-deadlock, worktree C:/Programs/f1-623)

## Task
Fix issue #623: `sampled-backtest`/`sampled-predict`/`gold-cycle` deadlocks at 0% CPU on the
first race when run headless (no controlling console/window-station — confirmed reproduced in
this exact worktree via a genuinely detached `Start-Process -WindowStyle Hidden` launch; see
`.agent-work/623-headless-deadlock/repro-evidence.md`). Root cause (verified against code):
`src/evo_predictor/module_runtime.py:194` (`loaded.module.predict(pair_batch.batch)`) is the
first real PyTorch forward pass in the process's lifetime; torch's native CPU thread pool
initializes lazily on that first big batched op, and that init path is console-handle-dependent
on Windows. `src/evo_predictor/run.py` currently does NOT import torch at all — but its own
import block transitively imports `src/latent_power/training.py` and
`src/evo_predictor/latent_power_bundle.py`, both of which `import torch` at module level, well
before `run_module_field` ever executes.

Fix: cap torch to a single thread, and cap the BLAS/OMP env vars, unconditionally at the very
top of `src/evo_predictor/run.py` — before any of its existing project imports (which
transitively trigger the first torch import) even run. This mirrors the exact pattern already
used in `src/utils/utilization.py:203-220` (`init_worker`), which does this same thing but only
inside `ProcessPoolExecutor` workers — never at the plain CLI entrypoint that the headless hang
actually goes through.

## Protected Intent
A headless (background task / `Start-Process -WindowStyle Hidden` / fully detached) invocation
of `py -m src.evo_predictor.run sampled-backtest ...` must complete instead of deadlocking.
Must not change any CLI argument, default, prediction output, or numeric behavior for any
existing caller — this is purely an execution-environment fix (thread count), not a behavior
change to what gets computed.

## Test Mode
Test-after allowed (bug fix at an entrypoint; the existing evo_predictor unit suite is the
regression backstop, plus one new small unit test asserting the entrypoint caps threads).

## Close Criteria
- `src/evo_predictor/run.py` sets `OMP_NUM_THREADS`, `MKL_NUM_THREADS`, `OPENBLAS_NUM_THREADS`,
  `NUMEXPR_NUM_THREADS` (via `os.environ.setdefault`, so an operator's own explicit override is
  still respected) and calls `torch.set_num_threads(1)`, all executed **before** any of the
  file's existing `from src....` project imports — i.e. inserted immediately after the stdlib
  imports (`argparse`/`json`/`logging`/`os`/`re`/`sys`/`dataclasses`/`datetime`/`pathlib`/
  `typing`) and before `import numpy as np` and the `from src.compound_prior...` block.
- The torch import/call is guarded (`try/except` around `import torch` +
  `torch.set_num_threads(1)`, catching a broad exception the way
  `src/utils/utilization.py:init_worker` does — torch may be absent for non-training tooling
  that imports `run.py`) so this file still imports cleanly in an environment without torch.
- This is unconditional — NOT gated on `sys.stdout.isatty()` or any other headless-detection
  heuristic (LAUNCH_ORDER Pre-Ruling #2).
- A new unit test (e.g. `tests/unit/evo_predictor/test_run_entrypoint_thread_cap.py`) asserts
  that importing `src.evo_predictor.run` results in `torch.get_num_threads() == 1` (import the
  module fresh, or assert directly if already imported in the test session — use
  `importlib.reload` if a prior test in the same session already set threads to something else,
  or simply assert the env vars are set as `os.environ["OMP_NUM_THREADS"] == "1"` if a true
  fresh-process reimport isn't practical inside the shared pytest session; pick whichever is
  robust and say which you picked).
- The full existing `tests/unit/evo_predictor/` + `tests/unit/test_utilization.py` suites stay
  green (no pre-existing test's behavior changes).

## Allowed Scope
- `src/evo_predictor/run.py` (the entrypoint fix only — the import-order block).
- One new test file under `tests/unit/evo_predictor/` (or an addition to
  `tests/unit/evo_predictor/test_run_cli_defaults.py` if that reads more naturally — your call).

## Specific Exclusions
- Do NOT touch `src/evo_predictor/module_runtime.py`, `src/evo_predictor/sampled_runtime.py`,
  `src/evo_predictor/sampled_backtest.py`, `src/evo_predictor/sampled_backtest_scoring.py`, or
  `src/utils/utilization.py` — this is a bounded fix at the CLI entrypoint only
  (LAUNCH_ORDER Pre-Ruling #3, this is a fenced exclusion owned by issue #623's launch order).
- Do NOT add an `isatty()`/headless-detection branch — the fix must apply unconditionally.
- Do NOT change any existing CLI argument default, or any production model default.

## Constraints
- Mirror `src/utils/utilization.py:203-220`'s guarded-import style (`try: import torch; ...
  except Exception: ...` with a `# noqa: BLE001`-style comment if this repo's lint config wants
  one — check `src/utils/utilization.py`'s exact comment for the convention to match) rather
  than inventing a new idiom.
- Use `os.environ.setdefault(...)`, not unconditional assignment, for the four env vars, so an
  operator who has deliberately set a different thread count is respected — but always call
  `torch.set_num_threads(1)` unconditionally (per Pre-Ruling #2, the torch call itself is not
  conditional; only the env-var respect-existing-value behavior uses `setdefault`).

## Map Anchors (inbound)
- **Structural:** `src/evo_predictor/run.py` — CLI entrypoint, module import order;
  `src/utils/utilization.py:203-220` (`init_worker`) — existing precedent pattern to mirror.
- **Capability:** `struct:evo` — CLI entrypoint only, no other capability touched.
- **Constraints/assumptions:** LAUNCH_ORDER Pre-Ruling #2 (unconditional fix, not isatty-gated);
  LAUNCH_ORDER Pre-Ruling #3 (bounded fix, no architecture refactor).
- **Evidence expectations:** `tests/unit/evo_predictor/` + `tests/unit/test_utilization.py`
  suites stay green.

## Deliverable Path Check
- **Committed** — `src/evo_predictor/run.py`; `git check-ignore -v src/evo_predictor/run.py`
  exited 1 (not ignored) — verified by the Commander before dispatch.
- **Committed** — `tests/unit/evo_predictor/test_run_entrypoint_thread_cap.py` (or wherever you
  land the new test); `git check-ignore -v tests/unit/evo_predictor/test_run_entrypoint_thread_cap.py`
  exited 1 (not ignored) — verified by the Commander before dispatch (this exact filename is a
  suggestion; if you name it differently, it is untracked until staged — new file appears in
  `git status`, not yet in a prior `git diff`).

## Required Evidence
- The full diff of `src/evo_predictor/run.py` (before/after the import block).
- The new/changed test file content.
- `py -m pytest tests/unit/evo_predictor tests/unit/test_utilization.py -q` output, tail
  included, with the final summary line (e.g. `NNN passed in Xs`) — run from
  `C:/Programs/f1-623` (this worktree), confirmed via
  `py -c "import src.evo_predictor.run as r; print(r.__file__)"` printing a path under
  `C:\Programs\f1-623` immediately beforehand (editable-install `.pth` worktree trap — verify
  you are testing your own code, not the main checkout's).

## Verification Commands

```bash
cd /c/Programs/f1-623
py -c "import src.evo_predictor.run as r; print(r.__file__)"
py -m pytest tests/unit/evo_predictor tests/unit/test_utilization.py -q
```

## Suggested Model Tier
Simple bounded — single-file, few-line, precedented fix plus one small test.

## Authority
The fix approach (unconditional torch.set_num_threads(1) + env vars at the top of run.py,
mirroring utilization.py's init_worker) is already decided by the Commander/Admiral launch
order — do not re-litigate the approach; implement it.

## Stop Conditions
Stop and return if: the fix cannot be made unconditional without breaking an existing test in a
way that reveals a real behavioral dependency on multi-threaded torch (this would be a
plan-invalidating discovery — return it, do not silently work around it); any file outside
Allowed Scope needs to change; a decision outside this handoff's authority is needed.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence
produced, assumptions used, stop conditions hit, out-of-scope observations, workflow feedback.
