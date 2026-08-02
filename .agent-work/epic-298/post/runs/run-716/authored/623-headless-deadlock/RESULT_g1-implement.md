# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g1-implement` (work-id `623-headless-deadlock`, branch `fix/623-headless-deadlock`, worktree `C:/Programs/f1-623`)

## Completed slice
Capped BLAS/OMP thread-pool env vars and torch's native thread pool unconditionally at the very
top of `src/evo_predictor/run.py` — before any of its project imports run (several of which
transitively `import torch` at module level). This closes the headless deadlock in issue #623:
torch's native CPU thread pool initializes lazily on its first big batched forward pass
(`module_runtime.py:194`), and that init path is console-handle-dependent on Windows — a fully
headless/detached launch (no controlling console/window-station) hung at 0% CPU the first time
it fired. The fix mirrors the existing precedent in `src/utils/utilization.py:203-220`
(`init_worker`), applied once, unconditionally, at the CLI entrypoint instead of only inside
`ProcessPoolExecutor` workers.

## Scope
**Files changed:**
- `src/evo_predictor/run.py` (the entrypoint fix, inserted after stdlib imports / before
  `import numpy as np`)
- `tests/unit/evo_predictor/test_run_entrypoint_thread_cap.py` (new test file)

**Specific exclusions touched:** no — `module_runtime.py`, `sampled_runtime.py`,
`sampled_backtest.py`, `sampled_backtest_scoring.py`, and `src/utils/utilization.py` were not
touched. No `isatty()`/headless-detection branch was added. No existing CLI argument default or
production model default was changed.

## Behavior changed
Yes, execution-environment only: any process that imports `src.evo_predictor.run` now runs with
BLAS/OMP/torch thread pools capped to 1 (unless the operator has already set those env vars
explicitly, via `os.environ.setdefault`). No change to CLI arguments, defaults, prediction
output, or numeric behavior for any caller — verified by the full regression suite staying green
(see Evidence).

## Map Impact
- **Structural anchors touched:** `src/evo_predictor/run.py` — CLI entrypoint import order;
  added an unconditional thread-cap block immediately after stdlib imports. No change to
  `struct:evo`'s public surface (CLI args, commands, or module registrations) — only its
  process-level execution environment.
- **Capabilities added/changed/affected:** none new; `struct:evo`'s CLI entrypoint now completes
  headlessly (issue #623) instead of deadlocking — an execution-reliability fix, not a new
  observable capability.
- **Constraints/assumptions touched:** LAUNCH_ORDER Pre-Ruling #2 (unconditional, not
  isatty-gated) and Pre-Ruling #3 (bounded fix, no architecture refactor) — both honored as
  specified.
- **Claims/evidence produced:** full `tests/unit/evo_predictor` + `tests/unit/test_utilization.py`
  suite (1978 passed / 19 skipped / 0 failed) confirms no CLI-argument, prediction-output, or
  numeric-behavior regression from the thread cap. Isolated timing of `test_metalearner.py`
  (the file real MLP training + 500-iteration bootstrap CI lives in) shows no meaningful
  slowdown from single-threading (8.22s without the fix vs 7.40s with it active) — see Stop
  Conditions Hit below for the full investigation this evidence resolves.
- **Trust limitations / drift found:** none in `run.py` itself. Found and fixed (in my own new
  test, not production code) a test-isolation hazard: `importlib.reload()` on a project module
  rebinds its module-level names to new objects in place, which can break `is`-identity
  assertions in *other* already-imported test modules holding stale `from X import Y` bindings.
  Worth a general note for anyone else tempted to use `importlib.reload` on a shared project
  module inside a test in this suite — flagging as a triage candidate below.
- **Triage candidates:** consider a lint/convention note (or a quick grep-based check) against
  `importlib.reload()` of shared `src/` modules inside `tests/unit/`, given the cross-test
  identity-pollution failure mode discovered here. Low priority — happened once, caught by the
  existing suite, fixed before it shipped.

## Test mode
**Required:** `test-after` (bug fix at an entrypoint; existing evo_predictor unit suite is the
regression backstop, plus one new small unit test).
**Satisfied:** yes — new test added (`test_run_entrypoint_thread_cap.py`, 2 tests), full
`tests/unit/evo_predictor` + `tests/unit/test_utilization.py` suite green.

## Evidence

Editable-install `.pth` worktree-identity check (run immediately before every test invocation
below):
```bash
cd /c/Programs/f1-623
py -c "import src.evo_predictor.run as r; print(r.__file__)"
```
Output: `C:\Programs\f1-623\src\evo_predictor\run.py` — confirmed testing this worktree's own
code, not the main checkout's.

**Full required suite** (handoff's exact Verification Commands, run in the foreground to avoid
this environment's background-task-reaping hazard — see Stop Conditions Hit):
```bash
cd /c/Programs/f1-623
py -m pytest tests/unit/evo_predictor tests/unit/test_utilization.py -q
```
Final summary line:
```
1978 passed, 19 skipped, 69 warnings in 284.07s (0:04:44)
```
**Result:** pass (0 failed). Run twice at this final state for reproducibility; both green.

**Bounded confirmation set** (entrypoint + module_runtime + sampled_backtest/runtime +
utilization, requested by a coordinating peer session as a faster spot-check):
```bash
cd /c/Programs/f1-623
py -m pytest tests/unit/evo_predictor/test_run_entrypoint_thread_cap.py tests/unit/evo_predictor/test_run_cli_defaults.py tests/unit/evo_predictor/test_module_runtime.py tests/unit/evo_predictor/test_sampled_backtest_runtime.py tests/unit/evo_predictor/test_sampled_runtime.py tests/unit/test_utilization.py -q --durations=10
```
Final summary line:
```
123 passed in 41.41s
```
**Result:** pass (0 failed).

**Full diff of `src/evo_predictor/run.py`:**
```diff
diff --git a/src/evo_predictor/run.py b/src/evo_predictor/run.py
index aee1bef1..ecfd70a8 100644
--- a/src/evo_predictor/run.py
+++ b/src/evo_predictor/run.py
@@ -14,6 +14,29 @@ from datetime import datetime, timezone
 from pathlib import Path
 from typing import Any, Dict, Mapping, Optional, Sequence
 
+# Cap BLAS/OMP thread pools and torch's native thread pool before any project import runs
+# (several transitively `import torch` at module level via src.latent_power.training /
+# src.evo_predictor.latent_power_bundle). Torch's CPU thread pool initializes lazily on its
+# first big batched forward pass, and that native init path is console-handle-dependent on
+# Windows: a fully headless/detached launch (no controlling console/window-station) deadlocks
+# at 0% CPU the first time it fires. Setting this unconditionally, at the top of the CLI
+# entrypoint, closes that hang regardless of caller (issue #623). `setdefault` respects an
+# operator's own explicit thread-count override; the torch call itself is unconditional.
+for _thread_env_var in (
+    "OMP_NUM_THREADS",
+    "MKL_NUM_THREADS",
+    "OPENBLAS_NUM_THREADS",
+    "NUMEXPR_NUM_THREADS",
+):
+    os.environ.setdefault(_thread_env_var, "1")
+
+try:
+    import torch
+
+    torch.set_num_threads(1)
+except Exception:  # noqa: BLE001 - torch may be absent for non-training tooling that imports run.py
+    logging.getLogger(__name__).debug("run: torch thread cap skipped", exc_info=True)
+
 import numpy as np
 
 from src.compound_prior.runtime_normalization import (
```

**New test file content** (`tests/unit/evo_predictor/test_run_entrypoint_thread_cap.py`):
```python
"""Regression test for issue #623 (headless deadlock).

`src/evo_predictor/run.py` must cap BLAS/OMP thread-pool env vars and torch's native thread
pool unconditionally, before any of its project imports run (those imports transitively
`import torch` at module level well before any prediction/training code executes). This
closes a Windows-only deadlock: torch's native CPU thread pool initializes lazily on its
first big batched forward pass, and that init path is console-handle-dependent — a fully
headless/detached launch hangs at 0% CPU the first time it fires.

Deliberately does NOT use `importlib.reload(src.evo_predictor.run)`: reload reruns the
module's top-level code in place, rebinding its module-level names (e.g. `cmd_sampled_backtest`,
`_build_parser`) to new function objects while other already-imported test modules hold
`from src.evo_predictor.run import ...` bindings to the pre-reload objects. That breaks
`is`-identity assertions elsewhere in the suite (observed: `test_sampled_backtest_cli.py`'s
`assert args.func is cmd_sampled_backtest` started failing once a reload-based version of this
test ran first in the same session). Plain import is sufficient: `src.evo_predictor.run` is
imported, directly or transitively, by many other test modules in this suite, so its
top-of-file thread-cap block has always already executed by the time this test body runs;
nothing else in the codebase calls `torch.set_num_threads` in the main test process (only
`src/utils/utilization.py`'s `init_worker`, which runs inside `ProcessPoolExecutor` worker
subprocesses, not here), so the effect is stable to assert on directly.
"""

from __future__ import annotations

import os

import torch

import src.evo_predictor.run  # noqa: F401 - imported for its side effect (thread cap)


def test_run_entrypoint_caps_torch_threads_on_import():
    assert torch.get_num_threads() == 1


def test_run_entrypoint_sets_thread_env_vars():
    # setdefault means an operator's own override is respected, so we only assert presence,
    # not the literal value "1" (a prior test/run in this process may have set a different
    # explicit value first, which the entrypoint must not clobber).
    for var in (
        "OMP_NUM_THREADS",
        "MKL_NUM_THREADS",
        "OPENBLAS_NUM_THREADS",
        "NUMEXPR_NUM_THREADS",
    ):
        assert var in os.environ, f"{var} was not set by importing src.evo_predictor.run"
```

## TDD evidence, if required
Not applicable — handoff Test Mode is test-after (collapsed to a single green postcondition,
per implementer plan template guidance for test-after runs). No TDD red step was recorded.

## Docs/contracts touched
- none (no CLI contract, report schema, or doc changed — pure execution-environment fix)

## Assumptions
- Picked "plain import + direct assert on `torch.get_num_threads() == 1`" over
  `importlib.reload` for the new test's robustness mechanism, per the handoff's own offered
  fallback ("or simply assert the env vars are set... pick whichever is robust and say which").
  This was not a free choice made in advance — the `reload`-based version was tried first (as
  literally suggested by the handoff's primary phrasing) and demonstrably broke
  `test_sampled_backtest_cli.py`'s identity assertion; the fallback was adopted after that
  failure was observed and diagnosed. See Stop Conditions Hit.
- Treated the four DB fixture files (`data/f1_data_2022.db` / `2023.db` / `2024.db` / `2025.db`)
  that showed as modified after running the full suite as a pre-existing test-run side effect
  unrelated to my change (out of Allowed Scope either way) and discarded them via
  `git checkout --` before finishing, at a coordinating peer session's request — consistent
  with Allowed Scope limiting changes to `run.py` and the one new test file.

## Stop conditions hit
None of the handoff's named stop conditions were ultimately triggered, but one was seriously
investigated and is worth recording in full:

- **Investigated, then ruled out:** "the fix cannot be made unconditional without breaking an
  existing test in a way that reveals a real behavioral dependency on multi-threaded torch."
  Three separate full-suite invocations appeared to hang/stall at ~37% (consistently inside
  `tests/unit/evo_predictor/test_metalearner.py`, which does real MLP training + a 500-iteration
  bootstrap CI and imports torch directly) — a strong prima facie match for this stop condition.
  Investigation: (1) isolated-file timing showed `test_metalearner.py` alone takes 8.22s without
  the fix and 9.00s with it present but not yet triggered (run.py not imported in that narrow
  invocation) — no signal; (2) forcing the fix to actually trigger first (via
  `test_gold_cycle_fingerprint.py`, which imports `src.evo_predictor.run`, run in the same
  process ahead of `test_metalearner.py`) still completed in 7.40s — no slowdown; (3) a full
  foreground run (not backgrounded) completed cleanly in 277-284s across three separate
  invocations. Conclusion: the repeated stalls were this environment's background-task-reaping
  behavior (documented project lesson "harness reaps long bg tasks + orphans children"), not a
  torch-single-threading performance regression — confirmed by a coordinating peer session
  independently finding and killing an orphaned pytest process (PID 2196) from one of the
  reaped attempts. Scope tested: this repo's evo_predictor + utilization unit suites on an
  8-core Windows box: single-threaded torch/BLAS does not measurably slow the heaviest CPU-bound
  test in that suite. Not tested: gold-cycle / integration-scale training runs, which were out
  of the handoff's required-evidence scope.
- **Real (different) issue found and self-corrected, not stopped on:** the first draft of the
  new test used `importlib.reload(src.evo_predictor.run)` and broke
  `test_sampled_backtest_cli.py::test_parser_accepts_sampled_backtest_args` (an `is`-identity
  assertion) via cross-module rebinding. This was caught by the full-suite run, diagnosed, and
  fixed within Allowed Scope (only the new test file changed) — not a plan-invalidating
  discovery about `run.py` itself, so work continued rather than stopping.

## Out-of-scope observations
- The four DB fixture files getting dirtied by a full unit-test run (independent of this
  change) is worth a look by whoever owns test fixture hygiene — not investigated further here,
  out of Allowed Scope.
- `importlib.reload()` of a shared `src/` module inside a test can silently break `is`-identity
  assertions in unrelated, already-imported test modules elsewhere in the suite (see Map Impact
  triage candidate above).

## Workflow Feedback
- **Handoff gaps:** none in the handoff's own text — task, scope, exclusions, evidence, test
  mode, and stop conditions were all complete and specific enough to execute directly (verified
  at `m0-context`).
- **Context rediscovered:** the handoff's `importlib.reload` suggestion (offered first, with
  the env-var-only assert as a named fallback) turned out to have a real, non-obvious cross-test
  side effect (breaking `is`-identity in an unrelated test file). This wasn't something the
  handoff could reasonably have anticipated — it's specific to this suite's mix of `from X
  import Y` bindings elsewhere — but it cost a full 5-minute suite run to discover.
- **Instructions improvised around:** the run environment itself does not support long
  backgrounded/detached test invocations reliably — three separate attempts (a `| tail -N`
  pipe that buffers until EOF and starves progress visibility, a `nohup ... &`+`disown`
  detachment, and the Bash tool's own `run_in_background`) all either stalled silently or were
  reaped/killed well before a ~5-minute test run finished. What worked: running the full
  command in the foreground, accepting the ~5-minute wait inside a single tool call (well under
  the 600s tool timeout). This is worth a durable note for future implementer runs in this repo
  hitting multi-minute `tests/unit/evo_predictor` invocations.
- **What would have made this easier:** a documented "how to run a 3-5 minute pytest command in
  this sandboxed environment without it being reaped" recipe (foreground-with-adequate-timeout,
  not background) would have saved the two failed background attempts and the resulting
  cross-session confusion about whether the fix was actually hung.

## Return status
`complete`
