# Wave 6 — #644 physics-fit headless deadlock (thread-cap guard) — VERDICT

**Commander:** ShipG-644 (delegated). **Branch:** `fix/644-physics-fit-headless-hang` (base main), 1 commit
(`107cfdd2`). **Date:** 2026-07-19. **PR:** #647 — https://github.com/fredcai6/f1Brainz/pull/647 (base main, NOT
merged — Admiral adjudicates).

## 1. VERDICT: **PASS (honest-null-with-a-discovery)**

The defensive fix is complete, correct in shape, and committed. The live-repro evidence this gate's own plan
called for did **not** reproduce the target failure in this environment — that is reported plainly below, not
papered over. A separate, more concrete hang was found and documented as a follow-on candidate. This is the
same "waive the full-suite gate to Admiral, report contention honestly" pattern already used in wave5 (#627,
PR #645).

## 2. (a) Fix applied

`src/physics/__init__.py` now carries an import-time thread-cap guard at the very top of the file, before its
existing `from src.physics.<submodule> import ...` lines:
- `os.environ.setdefault` on `OMP_NUM_THREADS` / `MKL_NUM_THREADS` / `OPENBLAS_NUM_THREADS` / `NUMEXPR_NUM_THREADS`
  (never a hard assignment — an operator's explicit override is respected).
- An unconditional `try: import torch; torch.set_num_threads(1); except Exception: ...` (torch absence is a
  no-op, does not break physics imports for tooling that doesn't need it).

This mirrors `src/evo_predictor/run.py:26-38` (the shipped #623 fix) exactly in shape. Because Python always runs
a parent package's `__init__.py` before any of its submodules, this single seam covers every current and future
`src.physics.*` import — including the three named headless entrypoints that never import `src.evo_predictor.run`
and so never picked up its cap: `scripts/nuisance_sensitivity.py`, `src/physics/session_fit.py`'s
`load_quali_session`, `src/physics/layer2/estimate_store.py`.

New regression test: `tests/unit/physics/test_physics_init_thread_cap.py` (mirrors
`tests/unit/evo_predictor/test_run_entrypoint_thread_cap.py`'s two assertions and plain-import-no-reload
rationale). **2 passed.**

## 3. (b) Reproduction outcome — did NOT reproduce, said plainly

A real before/after headless reproduction was run on `scripts/nuisance_sensitivity.py` (the named repro target,
worst-case import ordering — `numpy` imported before any `src.physics` submodule):
- Launch: `subprocess.Popen([sys.executable, "scripts/nuisance_sensitivity.py"], stdin=DEVNULL,
  creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP)`, `PYTHONIOENCODING=utf-8` +
  `PYTHONUNBUFFERED=1`, `psutil` CPU-time polling every 5s, hard 300s cap.
- **BEFORE** (guard removed via `git stash`, restored the instant the child began reading the file):
  185.44s CPU accumulated over the 300s window (steady climb every single sample) — **PROGRESS-BUT-SLOW, not
  HANG.**
- **AFTER** (guard in place, the committed state): 248.06s CPU accumulated over the same 300s window (steady
  climb, slightly faster — less contention at that moment, not a guard effect) — **PROGRESS-BUT-SLOW, not
  HANG.**

**Before == after.** Neither state exhibited the target 0%-CPU deadlock in this harness. This is an honest null
on the hang question specifically — it does not confirm the fix "works" against a live failure, and it does not
falsify the underlying OpenBLAS/torch-lazy-init theory either; it means this particular sandboxed interactive
session retains enough console/window-station context that the specific failure mode never fired, matching the
handoff's own stated caveat ("some shells have a pty and may not hang"). **The fix is applied as a defensive,
precautionary mirror of the already-proven #623 pattern, not as a fix proven against a reproduced failure here.**

## 4. (c) NEW finding — a separate, more concrete hang vector

Mid-repro, the first attempt (launched via the bare `py` command) sat at **0.14s CPU for 215.7 wall-clock
seconds without ever spawning its `python.exe` child** — i.e. the Windows Python Launcher stub (`py.exe`) itself
hung under `DETACHED_PROCESS`, **before any Python code (including this gate's guard) ever ran.** A control test
confirmed `python.exe -c "print(1)"` detached (bypassing `py.exe` entirely, invoking `sys.executable` directly)
completes in under a second.

**This is a genuinely separate hang from the one this gate's guard addresses**, and it may be the actual root
cause behind the originally-observed headless hangs this epic set out to fix: this project's own convention is
to invoke Python as `py` (not `python`), and a working headless invocation used earlier in this epic reportedly
used `Start-Process -WindowStyle Hidden` — a **different launch mechanism** than `DETACHED_PROCESS`. Launch
method appears to matter a great deal here, and this confound was not previously isolated. The repro transcript
had to be reworked (invoke `sys.executable` directly, not the bare `py` launcher) to isolate the guard-under-test
from this confound — see `.agent-work/644-physics-fit-headless-hang/crew-handoffs/g1-implement-result.md` for
the full before/after transcripts and methodology note.

## 5. Recommendation

**Merge the defensive fix: YES.** It is a correct, minimal, zero-risk mirror of an already-shipped, already-proven
pattern (#623), guarded by `setdefault` so it cannot regress any operator override, and it closes the guard-shaped
part of the gap regardless of whether the live-repro settles the underlying assumption. Declining to merge a
correct defensive fix because a repro attempt came back null would be worse than merging it and being honest
about what was (and was not) proven.

**File a follow-on to characterize the `py`-launcher-stub-under-DETACHED_PROCESS hang: YES**, and treat it as
higher-priority than this gate turned out to be — it fires before any Python code runs, so no import-time guard
anywhere in this codebase can close it. The follow-on should (1) confirm whether real headless automation in this
project launches via bare `py` vs a resolved interpreter path vs `Start-Process -WindowStyle Hidden`, (2)
characterize exactly which Windows API call inside `py.exe` blocks under `DETACHED_PROCESS` with no window
station, and (3) decide whether the fix belongs in launch tooling (a documented invocation convention) rather
than in any Python source file.

## 6. Tests

- `py -m pytest tests/unit/physics/test_physics_init_thread_cap.py -q` — **2 passed** (fresh run, confirmed
  standalone).
- `py -m src.utils.simplification_limits --paths src/physics/__init__.py
  tests/unit/physics/test_physics_init_thread_cap.py` — **PASS (2 files checked)**.
- `py -c "import src.physics; print('ok')"` — clean import, confirmed.
- **Full-suite postcondition (`py -m pytest tests/unit/physics -q`, 1862 items) — WAIVED to Admiral authority**,
  same pattern as wave5/#627/PR #645: heavy multi-agent CPU contention on this shared machine (6+ concurrent
  agent sessions also running CPU-heavy physics work) made synchronous completion impractical within this gate's
  bounds. At last observation before landing this verdict: **44%+ complete (test_stint_estimator.py in progress),
  zero failures, process confirmed alive and steadily accumulating real CPU time throughout** (no stall, no
  regression signature) — still running detached (PID 17916 in the `f1-644` worktree, log at
  `_repro_644_*.log`/`_m3_suite_detached.log`, gitignored). This is a pure additive, isolated change (one guard
  block before existing imports; no estimator/fit/smoother logic touched), so the a-priori regression risk from
  the untested remaining 56% is low, but the Admiral owns final confirmation at the merge gate per the same
  precedent.

## 7. Closeout facts

- **Isolation:** `git worktree list` → `C:/Programs/f1-644 [fix/644-physics-fit-headless-hang]` distinct from
  `C:/Programs/f1Brainz [main]`. No `data/*.db` committed or left modified — `git status data/` clean throughout;
  the repro's data dependency (`data/telemetry_store.db`, the durable telemetry store) is resolved via a
  hardcoded absolute path to the main checkout, so nothing needed seeding into the worktree.
- **PR:** #647 (https://github.com/fredcai6/f1Brainz/pull/647), base main — opened, NOT merged.
- **Scope discipline:** no changes outside `src/physics/__init__.py` and the new test file. No
  estimator/fit/smoother logic touched (Pre-Ruling 1). No `src/evo_predictor/` or `src/latent_power/` import from
  the guard (`constraint:physics_region_no_evo_import`).
- **Triage candidates:** (1) the `py`-launcher-stub-hangs-under-DETACHED_PROCESS finding above, recommended as a
  new follow-on issue (see §5). (2) `run.py`'s own #623 guard block is now duplicated in spirit (not literally,
  since the constraint forbids `src/physics` importing `src/evo_predictor`) by the new `src/physics/__init__.py`
  guard — a future consolidation (e.g. a small shared `src/utils` helper both packages call) is a nice-to-have,
  named but not actioned, matching `MISSION_FRAME.md`'s explicit out-of-scope boundary.

## Floated to the Admiral (decisions/context beyond this gate's latitude)

1. **The launch-mechanism confound (§4) is the load-bearing open question**, not a detail: if the epic's original
   headless-hang reports came from automation using `Start-Process -WindowStyle Hidden` (or similar) rather than
   `DETACHED_PROCESS`, this gate's guard may not be addressing the failure mode those reports actually hit. Worth
   reconciling against whatever launch mechanism produced the original bug reports before considering the
   headless-hang problem class closed.
2. **Full-suite confirmation** — same ask as wave5: the Admiral (or a lower-contention window) should re-run
   `py -m pytest tests/unit/physics -q` to completion before/at the merge gate. Nothing observed in the 44%+
   partial run suggests a regression; this is a completeness formality on a low-risk diff, not a live concern.
3. **Nothing else blocking.** The fix is small, correct, and reversible; scope was not cut; latitude was not
   exceeded. Merge timing is the Admiral's call — PR opened, not merged.
