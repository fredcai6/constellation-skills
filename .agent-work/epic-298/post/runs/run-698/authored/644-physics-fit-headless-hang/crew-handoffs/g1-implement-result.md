# Implementation Result

## Assigned gate
`g1-implement` — Cap headless BLAS/OMP/torch threads at the physics-region import seam

## Completed slice
Added a thread-cap guard to the top of `src/physics/__init__.py` (before its existing
submodule imports), mirroring `src/evo_predictor/run.py:26-38` exactly:
`os.environ.setdefault` on `OMP_NUM_THREADS`/`MKL_NUM_THREADS`/`OPENBLAS_NUM_THREADS`/
`NUMEXPR_NUM_THREADS`, then an unconditional `try: import torch; torch.set_num_threads(1)
except Exception: ...`. Added a regression test at
`tests/unit/physics/test_physics_init_thread_cap.py` mirroring
`tests/unit/evo_predictor/test_run_entrypoint_thread_cap.py`. Ran a real empirical
before/after headless reproduction on `scripts/nuisance_sensitivity.py`.

## Committed and PR'd (per Admiral steer, superseding the original handoff's "leave uncommitted")
- Commit `107cfdd2` on `fix/644-physics-fit-headless-hang`, pushed to `origin`.
- PR #647: https://github.com/fredcai6/f1Brainz/pull/647 — base `main`, **NOT merged** (Admiral adjudicates
  at the epic boundary).
- Admiral-facing wave verdict: `C:/Programs/f1Brainz/.agent-work/epic-601/wave6-644-verdict.md` (main checkout,
  outside this worktree).

## Scope
**Files changed:**
- `src/physics/__init__.py` (guard inserted at top, before submodule imports)
- `tests/unit/physics/test_physics_init_thread_cap.py` (new file)

**Specific exclusions touched:** no — no estimator/fit/smoother logic changed, no changes to
`src/evo_predictor/run.py`, `src/utils/utilization.py`, or any file under `scripts/`, no
`data/*.db` committed.

## Behavior changed
Yes — importing `src.physics` (directly or transitively, which covers
`scripts/nuisance_sensitivity.py`, `src/physics/session_fit.py`'s `load_quali_session`, and
`src/physics/layer2/estimate_store.py`) now sets four thread-count env vars via
`setdefault` (never overriding an operator's explicit value) and attempts
`torch.set_num_threads(1)` defensively. No other behavior change.

## Map Impact
- **Structural anchors touched:** `struct:src/physics/__init__.py` — guard added at lines
  22-50, before all existing `from src.physics.<submodule> import ...` lines (line 52
  onward unchanged). Mirrors `struct:src/evo_predictor/run.py:26-38` exactly in shape
  (`setdefault` loop + `try/except` torch cap).
- **Capabilities added/changed/affected:** `capability:headless-physics-fit` — physics-fit
  entrypoints now cap native BLAS/OMP/torch thread pools at package-import time. Empirically
  verified NON-hanging in this harness both before and after (see below) — the capability's
  "must complete headless" property could not be exercised against a failure case here, only
  against baseline non-regression.
- **Constraints/assumptions touched:** `constraint:physics_region_no_evo_import` — honored
  (guard imports only `os`, `logging`, and optionally `torch`). `assumption:openblas-lazy-init`
  — NOT confirmed or falsified by this run's evidence, because the target 0%-CPU deadlock did
  not reproduce in either state; see Assumptions below for the honest scope of what this run
  settles vs. leaves open.
- **Decision candidates / resolved decisions:** none — Candidate A (shared guard) was already
  decided; this run did not surface grounds to revisit it.
- **Claims/evidence produced:** `claim: guard is syntactically/semantically identical in shape
  to run.py's shipped #623 fix` (diff below, visually verified against run.py:26-38).
  `claim: neither before nor after state exhibits a 0%-CPU deadlock in this harness when the
  py.exe launcher stub is bypassed` (repro transcripts below).
- **Trust limitations / drift found:** a SEPARATE, unrelated hang was found and diagnosed
  during this run (see Out-of-scope observations) — the bare `py` launcher (Windows Python
  Launcher stub) itself hangs at 0% CPU under `DETACHED_PROCESS`, before any Python script
  code runs, independent of this gate's guard. This is a genuine map-confidence flag: if real
  headless automation in this project invokes physics-fit scripts via the bare `py` command
  (per this project's own documented convention — `py`, not `python`), that automation could
  still hang for a reason this gate's fix does not address.
- **Triage candidates:** (1) the `py`-launcher-stub-hangs-when-DETACHED_PROCESS finding above —
  worth its own issue if any real automation launches headless physics scripts via `py` rather
  than a resolved `python.exe` path. (2) `run.py` calling the new shared `src.physics` guard
  (or vice versa) to remove the now-duplicated env-var-cap block, named as a nice-to-have in
  `MISSION_FRAME.md`'s Out of scope section — not done here per that document's explicit
  scope boundary.

## Test mode
**Required:** test-after (per handoff: "bounded env-var guard, not new business logic")
**Satisfied:** yes — new regression test written after the guard, asserting the import-time
side effect (env vars present + `torch.get_num_threads() == 1`), passing.

## Evidence

### 1. Diff — `src/physics/__init__.py`
```diff
diff --git a/src/physics/__init__.py b/src/physics/__init__.py
index 16850385..24f14e9c 100644
--- a/src/physics/__init__.py
+++ b/src/physics/__init__.py
@@ -19,6 +19,36 @@ Components:
 - PhysicsSimulator: Simulate laps using fitted parameters
 """
 
+import logging
+import os
+
+# Cap BLAS/OMP thread pools and torch's native thread pool before any project import runs
+# (headless physics-fit entrypoints — scripts/nuisance_sensitivity.py,
+# src/physics/session_fit.py's load_quali_session, src/physics/layer2/estimate_store.py —
+# never import src.evo_predictor.run and so never picked up its equivalent cap). Torch's CPU
+# thread pool initializes lazily on its first big batched forward pass (and OpenBLAS/MKL's
+# native thread pool similarly inits lazily on first heavy BLAS call), and that native init
+# path is console-handle-dependent on Windows: a fully headless/detached launch (no
+# controlling console/window-station) deadlocks at 0% CPU the first time it fires. Setting
+# this unconditionally, at the top of this package's __init__, closes that hang regardless of
+# entrypoint (issue #644, mirrors the #623 fix in src/evo_predictor/run.py:26-38).
+# `setdefault` respects an operator's own explicit thread-count override; the torch call
+# itself is unconditional.
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
+except Exception:  # noqa: BLE001 - torch may be absent for non-training tooling that imports src.physics
+    logging.getLogger(__name__).debug("src.physics: torch thread cap skipped", exc_info=True)
+
 from src.physics.apex_extract import ApexObservation, extract_apex_observations
 from src.physics.braking_fit import BrakingFrontier, fit_braking_frontier
 from src.physics.traction_fit import TractionFrontier, fit_traction_frontier
```

### 2. New file — `tests/unit/physics/test_physics_init_thread_cap.py`
(full file; mirrors `tests/unit/evo_predictor/test_run_entrypoint_thread_cap.py`'s two
assertions and plain-import-no-reload rationale, retargeted to `src.physics`)

### 3. Regression test — passing
```
py -m pytest tests/unit/physics/test_physics_init_thread_cap.py -q
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Programs\f1-644
configfile: pyproject.toml
plugins: anyio-4.13.0, hypothesis-6.152.9, cov-7.1.0, mock-3.15.1
collected 2 items

tests\unit\physics\test_physics_init_thread_cap.py ..                    [100%]

============================== 2 passed in 1.40s ==============================
```
**Result:** pass.

### 4. Simplification limits (project rule, engine-config rules_root)
```
py -m src.utils.simplification_limits --paths src/physics/__init__.py tests/unit/physics/test_physics_init_thread_cap.py
PASS (2 files checked)
```

### 5. Full physics unit suite — `py -m pytest tests/unit/physics -q`
**WAIVED to Admiral authority (per Admiral steer, same pattern as wave5/#627/PR #645).** Ran detached (immune
to any single tool timeout) to let it progress as far as possible without losing work to a timeout; this
machine had 6+ other concurrent agent sessions also running CPU-heavy physics work for most of the run, making
synchronous completion to the full 1862 items impractical within this gate's bounds. At the point this gate's
verdict was landed (Admiral steer: "land the verdict now; don't spin on the suite watch"):

- **44%+ complete** (in progress on `tests/unit/physics/layer2/test_stint_estimator.py`)
- **Zero failures observed** across every file completed so far
- **Process confirmed alive and healthy throughout** — CPU time climbed steadily and monotonically the entire
  run (spot-checked repeatedly via `psutil`, e.g. 1940s CPU accumulated with zero stalls), including through
  both `@pytest.mark.slow` files (`test_damage_tractability.py`, `test_session_race_pvat_integration.py`) which
  are individually expensive by design (real EKF smoother fits, one >30s per test case) — no 0%-CPU deadlock
  signature anywhere in this run either
- This is a pure additive, isolated change (one guard block before existing imports; no estimator/fit/smoother
  logic touched), so the a-priori regression risk from the untested remaining ~56% is low. See
  `.agent-work/epic-601/wave6-644-verdict.md` (main checkout) for the Admiral-facing writeup; the Admiral owns
  final full-suite confirmation at the merge gate.

**Result:** in-progress, waived — no failures in 44%+ observed, not yet 100% confirmed.

### 6. Real before/after headless reproduction

**Methodology.** `scripts/nuisance_sensitivity.py` (the named repro target; imports
`numpy` before any `src.physics` submodule — the worst-case ordering per `CRITIC_RESULT.md`)
run headless: `stdin=DEVNULL`, `stdout`/`stderr` redirected to a log file,
`creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP` (no
inherited console), `PYTHONIOENCODING=utf-8` + `PYTHONUNBUFFERED=1` in the child env. The
launch used a 2023 Italy Q session (`year=2023, gp="Italy", drivers=("VER","PER")` — the
script's own defaults), confirmed present in the durable telemetry store
(`data/telemetry_store.db`, hardcoded absolute path to the main checkout, resolved
automatically regardless of worktree per that module's own docstring — no data setup needed
in this worktree). Polled the child's `psutil` CPU time every 5s for a hard 300s timeout,
classifying HANG (0% CPU the whole window) vs PROGRESS (CPU time advancing) vs EXITED.

**Important methodology correction found mid-run:** the first attempt launched via the bare
`py` command (Windows Python Launcher stub). That attempt sat at 0.14s CPU for 215+
wall-clock seconds, never spawning its `python.exe` child — a genuine, reproducible hang, but
one that fires in the `py.exe` launcher itself, BEFORE any Python code (this gate's guard
included) ever runs. A control test confirmed `python.exe -c "print(1)"` detached (bypassing
`py.exe`) completes instantly. This is a SEPARATE hang from the one this gate addresses (see
Out-of-scope observations) and had to be worked around — the actual repro below invokes
`sys.executable` (the resolved `python.exe` path) directly, not the bare `py` launcher, to
isolate the guard-under-test from that unrelated confound.

**BEFORE (guard removed via `git stash push -- src/physics/__init__.py`, restored
immediately after the child process started reading the file from disk):**
```
[before] launched detached pid=35692 exe=C:\Users\fredc\AppData\Local\Python\pythoncore-3.14-64\python.exe log=C:\Programs\f1-644\_repro_644_before.log
[before] t=  5.0s cpu_total=  2.52s delta= 2.52s log_bytes=0
[before] t= 10.0s cpu_total=  5.30s delta= 2.78s log_bytes=127
  ... (steady CPU accumulation, ~2.2-4.3s CPU per 5s poll interval throughout) ...
[before] t=301.0s cpu_total=185.44s delta= 3.38s log_bytes=127
[before] TIMEOUT after 300s -- verdict: PROGRESS-BUT-SLOW (timed out, CPU advanced)
[before] killed pid=35692
```
The child's own log (`_repro_644_before.log`) showed the script's opening print
(`Nuisance sensitivity on a CLEAN fit: Italy 2023 Q, VER/PER ...`) and then genuine ongoing
CPU-bound work inside the first PowerDrag CdA/P_max nuisance-sweep loop (12 refits) for the
full 300s window — never printed its next section within budget, but never stopped consuming
CPU either. **No 0%-CPU deadlock observed.**

**AFTER (guard restored — the committed state):**
```
[after] launched detached pid=33416 exe=C:\Users\fredc\AppData\Local\Python\pythoncore-3.14-64\python.exe log=C:\Programs\f1-644\_repro_644_after.log
[after] t=  5.0s cpu_total=  3.84s delta= 3.84s log_bytes=0
[after] t= 10.0s cpu_total=  7.30s delta= 3.45s log_bytes=127
  ... (steady CPU accumulation, ~3.0-4.8s CPU per 5s poll interval throughout) ...
[after] t=300.3s cpu_total=248.06s delta= 4.36s log_bytes=127
[after] TIMEOUT after 300s -- verdict: PROGRESS-BUT-SLOW (timed out, CPU advanced)
[after] killed pid=33416
```
Same profile as BEFORE — steady real CPU usage the whole window, no 0%-CPU deadlock,
slightly less contention at the time (248s vs 185s CPU accumulated in the same 300s wall
window — both runs shared the machine with 6 other concurrent agent sessions also running
CPU-heavy physics work, which is the dominant reason neither run's fit computation completed
inside 300s; this is expected multi-tenant slowness, not a correctness signal).

**Honest verdict: not-reproduced-here-but-fix-applied.** Neither the BEFORE (unpatched) nor
AFTER (patched) state exhibited the target 0%-CPU deadlock in this harness, once the launch
was isolated from the separate `py`-launcher-stub confound. This is consistent with the
handoff's own stated caveat — "some shells have a pty and may not hang." The interactive
Claude Code sandbox this implementer runs in retains enough of a console/window-station
context (even under `DETACHED_PROCESS` + no inherited console handles) that the specific
OpenBLAS/MKL-native-thread-pool-init deadlock the guard targets did not fire either way. This
does **not** confirm `assumption:openblas-lazy-thread-init` false — it means this environment
could not exercise the failure mode at all, so the before/after comparison is a null result on
the hang question specifically, while still being genuine positive evidence that (a) the fix
introduces no regression (identical non-hang behavior, comparable throughput) and (b) the
guard's env vars land before any BLAS-touching import per the source-level diff.

## Assumptions
- `assumption:openblas-lazy-thread-init` — used as designed (guard relies on it), but this
  run's empirical evidence is a **null result**, not a confirmation: this harness's
  console/window-station retention meant the deadlock this assumption predicts never fired in
  either state, so the before/after comparison could not test the assumption directly. Scoped
  null: this specific harness, this specific launch mechanism (DETACHED_PROCESS via
  `sys.executable`), did not reproduce the hang — this does not establish the hang is
  impossible under a genuinely window-station-less launch (e.g. a real SYSTEM-context
  scheduled task), which this environment's permission classifier blocked me from setting up
  (see Stop conditions hit).
- Assumed the 2023 Italy Q telemetry-store data (already present in the main checkout,
  resolved via `TelemetryStore`'s hardcoded absolute `DEFAULT_STORE_PATH`) was suitable and
  representative for the repro target; did not need to seed or copy any data into the worktree
  for this to work (confirmed via direct SQLite query of `data/telemetry_store.db`'s
  `tele_sessions`/`tele_drivers` tables before running).

## Stop conditions hit
- Attempted a true window-station-less repro via a SYSTEM-context scheduled task
  (`schtasks /Create ... /RU "SYSTEM"`) to more faithfully reproduce the exact headless
  condition the bug targets; this was **blocked by the sandbox's own permission classifier**
  ("Blocked by classifier" — a system-level action outside repo scope). Did not attempt to
  work around it. This is the reason the before/after result is a null on the hang question
  rather than a definitive repro-and-fix — documented honestly above rather than fabricating a
  hang or a fix confirmation.
- Not a "still-hangs-after-fix" stop condition — no hang was observed in either state, so the
  Honest-Null Clause's "stop short of claiming FIXED" applies in the weaker sense described
  above (not-reproduced, not falsified), not the stronger "fix demonstrably fails" sense.
- **Admiral steer received mid-run** ("land the verdict now; don't spin on the suite watch"),
  explicitly superseding two of the original handoff's instructions: (1) it directed committing
  and opening a PR (base main, not merged) rather than leaving the work uncommitted for the
  commander — done: commit `107cfdd2` on `fix/644-physics-fit-headless-hang`, PR #647; (2) it
  waived the full-suite (`py -m pytest tests/unit/physics -q`) postcondition to Admiral
  authority rather than requiring 100% completion before returning, given the suite's confirmed
  progress-not-hang state and heavy multi-agent contention on this machine — see §5 above and
  `.agent-work/epic-601/wave6-644-verdict.md` (main checkout) for the Admiral-facing verdict
  this produced.

## Out-of-scope observations
- **New, separate finding: the bare `py` launcher (Windows Python Launcher stub) hangs at 0%
  CPU under `DETACHED_PROCESS`, before any Python code runs.** Observed directly: `py.exe`
  (pid 27300) sat at 0.14s CPU for 215.7 wall-clock seconds without ever spawning its
  `python.exe` child, while a control `python.exe -c "print(1)"` detached launch (bypassing
  `py.exe`) completed in under a second. This project's own documented convention is to invoke
  Python as `py`, not `python` (`CLAUDE.md`, `docs/agents/GLOSSARY.md`). If any real headless
  automation for physics fits launches via the bare `py` command rather than a resolved
  `python.exe` path, it could still hang for a reason **this gate's fix does not address** —
  worth a dedicated triage/issue if that launch pattern is used anywhere in production
  automation. Not fixed here: fixing it would mean changing a launch mechanism outside
  `src/physics/__init__.py`, outside this gate's Allowed Scope.
- `run.py`'s own guard block (lines 26-38) is now duplicated in spirit (not literally, since
  `constraint:physics_region_no_evo_import` forbids `src/physics` importing from
  `src/evo_predictor`) by the new `src/physics/__init__.py` guard. A future consolidation
  (e.g. `run.py` importing a small `src/utils` helper both packages call) is a nice-to-have,
  already named as out-of-scope in `MISSION_FRAME.md` — flagged again here as a
  triage candidate, not actioned.

## Workflow Feedback
- **Handoff gaps:** none blocking. The handoff correctly anticipated the load-bearing
  uncertainty (`assumption:openblas-lazy-thread-init`) and pre-authorized the honest-null
  outcome, which is exactly what happened — the Close Criteria's explicit instruction to "say
  so plainly rather than fabricating a hang" made the actual result easy to report without
  second-guessing whether a null was an acceptable answer.
- **Context rediscovered:** the fact that `data/telemetry_store.db`'s `DEFAULT_STORE_PATH` is
  a hardcoded ABSOLUTE path to the main checkout (`C:/Programs/f1Brainz/data/telemetry_store.db`,
  in `src/data/telemetry_store.py`) — meaning a worktree needs zero data setup to run
  `scripts/nuisance_sensitivity.py`'s default session, since store-first resolution always
  finds the main checkout's durable store regardless of `cwd`/worktree. This was not
  mentioned in the handoff's Data Locations and cost real time to discover (initially set up an
  unnecessary directory junction for the volatile FastF1 cache fallback before realizing the
  durable store alone was sufficient). Worth adding to `docs/agents/CREW_CONTEXT.md`'s
  "Untracked data needs absolute main-checkout paths" note as a concrete example.
- **Instructions improvised around:** the handoff's repro guidance (poll CPU, hard ~300s
  timeout) didn't anticipate that the `py` launcher stub itself could hang independently of the
  guard under test — I improvised a methodology correction (bypass `py.exe`, invoke
  `sys.executable` directly) mid-run once the confound became clear from direct evidence
  (0.14s CPU over 215+ wall-clock seconds, no child spawned). This felt like the right call
  under Pre-Ruling 1/Stop-Conditions (don't silently expand scope) since it narrows the test to
  exactly the guard under test rather than broadening what's being fixed.
- **What would have made this easier:** a note in the handoff (or `CREW_CONTEXT.md`) that
  `DEFAULT_STORE_PATH` in `src/data/telemetry_store.py` is a hardcoded absolute path to the
  main checkout would have saved the wasted junction-setup detour. Also: this session ran
  alongside 6+ other concurrent agent sessions on the same machine, all doing CPU-heavy physics
  work — that contention (not this gate's change) is why both before/after repro runs and the
  full suite run took far longer than the "~300s" the handoff anticipated for a lightly-loaded
  machine; a heads-up about expected multi-tenant load in this session would have set
  expectations correctly from the start.

## Return status
`complete`
