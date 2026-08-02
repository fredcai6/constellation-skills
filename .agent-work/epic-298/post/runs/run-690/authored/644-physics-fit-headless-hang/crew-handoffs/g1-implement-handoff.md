# Implementer Handoff

## Gate
`g1` (execute.json: g1-implement)

## Task
Add a headless thread-cap guard to `src/physics/__init__.py` (top of file, before its existing
submodule imports) that caps `OMP_NUM_THREADS` / `MKL_NUM_THREADS` / `OPENBLAS_NUM_THREADS` /
`NUMEXPR_NUM_THREADS` and torch's native thread pool, mirroring the shipped #623 fix in
`src/evo_predictor/run.py:26-38` exactly. This closes the deadlock class where headless
physics-fit entrypoints (`scripts/nuisance_sensitivity.py`, `src/physics/session_fit.py`'s
`load_quali_session`, `src/physics/layer2/estimate_store.py`) hang at ~0% CPU on Windows
because they never import `run.py` and so never get the existing cap.

## Protected Intent
Headless physics fits must complete (not hang at 0% CPU). Interactive/console physics runs
must be unaffected in behavior beyond thread count (the cap is `setdefault`-based so an
operator's own explicit thread-count env var is respected, same as `run.py`).

## Test Mode
Test-after allowed, mirroring the existing #623 regression test's own pattern (a small
deterministic unit test asserting the import-time side effect) — this is a bounded env-var
guard, not new business logic; TDD adds no value over asserting the resulting env state.

## Close Criteria
- `src/physics/__init__.py` sets the four env vars via `os.environ.setdefault` and attempts
  `torch.set_num_threads(1)` inside `try/except Exception`, all BEFORE its first existing
  `from src.physics.<submodule> import ...` line.
- A new regression test at `tests/unit/physics/test_physics_init_thread_cap.py` (mirror
  `tests/unit/evo_predictor/test_run_entrypoint_thread_cap.py` almost verbatim — same two
  assertions, same "plain import, no importlib.reload" rationale — but importing
  `src.physics` instead of `src.evo_predictor.run`, and with a docstring naming #644/#623 and
  the physics entrypoints this closes) passes.
- **The load-bearing evidence for this gate is empirical, not just the test:** attempt a
  REAL before/after headless reproduction on `scripts/nuisance_sensitivity.py` (or the
  smallest physics-fit call you can run standalone) with a hard wall-clock timeout (~300s),
  polling CPU usage to distinguish a 0%-CPU deadlock from slow-but-progressing computation.
  - **Before the fix** (on a clean checkout of the current file, or via `git stash`): does it
    hang at ~0% CPU headless? Document what you observed, honestly — including if you cannot
    reproduce a hang in this shell (some shells have a pty and may not exhibit the Windows
    headless-deadlock condition; say so plainly rather than fabricating a hang).
  - **After the fix**: does the SAME command now complete (CPU > 0 at some point, process
    exits 0, artifact produced)? This is the check that settles whether the assumption this
    plan rests on — OpenBLAS/MKL's native thread pool inits LAZILY on first heavy BLAS call
    (matching `run.py`'s own comment about torch's lazy first-forward-pass init), not eagerly
    at `import numpy` — actually holds. **48 of the ~51 physics-touching scripts under
    `scripts/` import numpy/pandas BEFORE any `src.physics` submodule** (verified by the
    commander via a repo-wide grep before this handoff was written), so if the eager-init
    reading is correct instead, this fix would NOT close the hang for `nuisance_sensitivity.py`
    despite closing it in the unit test's narrower "does `src.physics.__init__` set env vars"
    sense.
- **If the post-fix real repro still hangs:** STOP short of claiming this gate FIXED. Per the
  launch order's Honest-Null Clause, do not fall back to patching all 48 scripts. Instead
  produce a precise diagnosis (what IS still blocking — is it really BLAS thread-pool init, or
  something else entirely, e.g. a different native library, stdin/stdout buffering, a
  subprocess call inside the fit) and return that as a blocker with your recommendation; the
  commander will float it to the Admiral rather than expanding scope unilaterally.

## Allowed Scope
- `src/physics/__init__.py` (the guard, inserted at the top)
- `tests/unit/physics/test_physics_init_thread_cap.py` (new file)
- Read-only inspection of `scripts/nuisance_sensitivity.py`, `src/physics/session_fit.py`,
  `src/physics/layer2/estimate_store.py`, `src/evo_predictor/run.py`,
  `tests/unit/evo_predictor/test_run_entrypoint_thread_cap.py` for the pattern to mirror.

## Specific Exclusions
- No changes to any estimator, smoother, fit, or view logic anywhere under `src/physics/`
  (Pre-Ruling 1). No changes to `src/evo_predictor/run.py` itself, `src/utils/utilization.py`,
  or any file under `scripts/` (even if the empirical repro reveals the eager-init case — that
  is a STOP-and-report condition, not a scope-expansion license).
- No changes to `src/evo_predictor/` or `src/latent_power/` (`constraint:physics_region_no_evo_import`
  — the guard itself must import only `os`, `logging`, and optionally `torch`).
- Do not commit any `data/*.db` file your reproduction run may touch — run
  `git status`/`git checkout -- data/` after any real fit run per #632.

## Constraints
- `os.environ.setdefault` (never a hard `os.environ[var] = ...`) on all four thread-count
  env vars, so an operator's explicit override is respected — exact mirror of `run.py:26-38`.
- The `torch.set_num_threads(1)` call is unconditional inside a `try/except Exception` (torch
  absence must not break physics imports for tooling that doesn't need it) — same shape as
  `run.py`. Do not gate the cap on `sys.stdout.isatty()` or any other conditional (Pre-Ruling
  2: unconditional).
- Python launcher on this machine is `py`, not `python` (lesson:py-launcher).
- `PYTHONIOENCODING=utf-8` on any captured subprocess you spawn for the repro.

## Map Anchors (inbound)
- **Structural:** `struct:src/physics/__init__.py` (guard target), `struct:src/evo_predictor/run.py:26-38` (pattern to mirror), `struct:scripts/nuisance_sensitivity.py` (repro entrypoint)
- **Capability:** `capability:headless-physics-fit` — a physics estimator fit must complete headless (no controlling console/window-station)
- **Constraints/assumptions:** `constraint:physics_region_no_evo_import`; `assumption:openblas-lazy-thread-init` — UNVERIFIED, this gate's job is to verify it empirically
- **Decision anchors:** guard placed once at `src/physics/__init__.py` (Candidate A), converged in `.agent-work/644-physics-fit-headless-hang/PLAN_ALTERNATIVES.md`, re-confirmed in `CRITIC_RESULT.md` after a cold-critic pass
- **Evidence expectations:** `run.py:26-38` guard shape (verified against source already — trust this citation, it has been independently re-verified twice); no `torch` import anywhere under `src/physics/` (verified, grep empty); 48/51 physics scripts import numpy before `src.physics` (verified by commander grep) — this is WHY empirical repro, not import-order reasoning alone, is the close criterion
- **Map confidence flags:** `assumption:openblas-lazy-thread-init` is the single load-bearing unverified claim this whole plan rests on — verify it for real, do not assume it

## Deliverable Path Check
- **Committed** — `src/physics/__init__.py`; `git check-ignore -v src/physics/__init__.py` exited 1 (not ignored).
- **Committed** — `tests/unit/physics/test_physics_init_thread_cap.py` (new file); `git check-ignore -v tests/unit/physics/test_physics_init_thread_cap.py` exited 1 (not ignored). It will not appear in `git diff` until staged — expect it in `git status` as untracked, then staged at commit.

## Required Evidence
- Full diff of `src/physics/__init__.py` and the new test file.
- `py -m pytest tests/unit/physics/test_physics_init_thread_cap.py -q` output (pass).
- `py -m pytest tests/unit/physics -q` output (full physics suite, pass — no regression).
- The real before/after reproduction transcript: exact command(s) run, wall-clock/CPU
  observations, and an honest verdict (reproduced-and-fixed / not-reproduced-here-but-fix-
  applied / still-hangs-after-fix).

## Verification Commands

```bash
py -m pytest tests/unit/physics/test_physics_init_thread_cap.py -q
py -m pytest tests/unit/physics -q
```

## Suggested Model Tier
Simple bounded — small, well-specified diff with a clear precedent to mirror; the only real
risk is the empirical-verification discipline, which is a process requirement, not a
complexity one.

## Authority
Seam placement (Candidate A: shared guard in `src/physics/__init__.py`, not per-script
patches) is already decided by the commander via design-it-twice + cold critic — do not
re-litigate it. If the empirical repro falsifies `assumption:openblas-lazy-thread-init`, do
NOT unilaterally switch to per-script patches — that is outside this gate's authority; stop
and report per Close Criteria.

## Stop Conditions
Stop and return if: the post-fix real repro still hangs (Honest-Null — report, do not silently
expand scope); a decision to touch files outside Allowed Scope seems necessary; required
evidence (the real repro) cannot be produced in this environment at all — say so honestly
rather than fabricating a hang or a fix confirmation.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence
produced (paste full pytest output AND the real repro transcript), assumptions used, stop
conditions hit, out-of-scope observations, workflow feedback.
