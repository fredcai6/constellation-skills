# Ship A verdict — issue #623 headless deadlock

## 1. VERDICT

**FIXED.** Headless backtest completes. `torch.set_num_threads(1)` + BLAS/OMP env-var caps,
applied unconditionally at the top of `src/evo_predictor/run.py`, close the deadlock. Fix
committed, reviewed (independent clean-room APPROVE), and — per `ADMIRAL_LOG.md` — already
squash-merged to `main` as PR #633 (commit `16c314b9`) and issue #623 closed. This verdict is
written retroactively/in parallel with that merge (see §7 "End-of-run anomaly" for why) but
documents my own independent chain of evidence, which corroborates the Admiral's.

## 2. Isolation evidence (at time of work, before the worktree was swept)

```
$ git rev-parse --abbrev-ref HEAD
fix/623-headless-deadlock
$ git worktree list
C:/Programs/f1Brainz c62a6430 [main]
C:/Programs/f1-623   c62a6430 [fix/623-headless-deadlock]
$ py -c "import src.evo_predictor.run as r; print(r.__file__)"
C:\Programs\f1-623\src\evo_predictor\run.py
```
All work (fix authorship, both crew dispatches, all four verification runs) happened with cwd
= `C:/Programs/f1-623`, confirmed via the worktree-identity check before every test invocation
(see the harvested `RESULT_g1-implement.md` / `RESULT_g1-review.md` for the crews' own repeated
checks of this).

## 3. The fix

`src/evo_predictor/run.py`, 23 lines added, nothing removed, inserted immediately after the
stdlib imports and before `import numpy as np` / any `from src....` import:

```python
for _thread_env_var in (
    "OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "NUMEXPR_NUM_THREADS",
):
    os.environ.setdefault(_thread_env_var, "1")

try:
    import torch
    torch.set_num_threads(1)
except Exception:  # noqa: BLE001 - torch may be absent for non-training tooling that imports run.py
    logging.getLogger(__name__).debug("run: torch thread cap skipped", exc_info=True)
```

Why: `src/evo_predictor/module_runtime.py:194` (`loaded.module.predict(pair_batch.batch)`) is
the first real PyTorch forward pass in the process's lifetime. Torch's native CPU thread pool
initializes lazily on that first big batched op, and that init path is console-handle-dependent
on Windows — a fully headless/detached launch (no controlling console/window-station) deadlocks
at 0% CPU the first time it fires. `run.py` itself never imported torch directly, but its own
import block transitively imports `src/latent_power/training.py` and
`src/evo_predictor/latent_power_bundle.py`, both of which `import torch` at module level — so
the cap has to land before those run, not inside `module_runtime.py` at the call site itself.
Mirrors the existing precedent in `src/utils/utilization.py:203-224` (`init_worker`), which does
the identical thing but only inside `ProcessPoolExecutor` workers — this applies it once,
unconditionally, at the CLI entrypoint (per LAUNCH_ORDER Pre-Ruling #2: not gated on
`isatty()`). New regression test: `tests/unit/evo_predictor/test_run_entrypoint_thread_cap.py`
(asserts `torch.get_num_threads() == 1` and all four env vars present after import).

New test file added: `tests/unit/evo_predictor/test_run_entrypoint_thread_cap.py`. No other
production file touched (`module_runtime.py`, `sampled_runtime.py`, `sampled_backtest.py`,
`sampled_backtest_scoring.py`, `src/utils/utilization.py` all untouched, per Pre-Ruling #3).

## 4. Verification

**Pre-fix reproduction** (genuinely detached `Start-Process -WindowStyle Hidden`, no console,
cwd = worktree, on the unmodified branch HEAD before any fix commit):
- Solo 1-race run (Bahrain, 2024): completed cleanly in 4m — did **not** reproduce the hang on
  the first attempt (noted honestly, per scoped-nulls doctrine).
- Two concurrent detached processes (matches the issue's own repro matrix: "two concurrent
  processes"): the Bahrain leg **deadlocked** — log froze at `race 1/1 - round 1 Bahrain
  (elapsed 0m, ETA ~0m)`, CPU/working-set flat (`CPU=0.15625s`, `WS=16MB`) across 26 consecutive
  30s polls (13 minutes wall-clock), never advanced, no output file ever written. Killed
  manually. This is the exact deadlock signature from #623 ("CPU=0 at race 1 start"). Full
  detail in `repro-evidence.md` (harvested into `.agent-work/623-headless-deadlock/` in this
  checkout).

**Post-fix verification** (same detached regime, fix applied):
- Concurrent pair #1 (Bahrain + a mistyped race name that crashed instantly): Bahrain leg
  **completed** cleanly in 4m, valid output (`aggregate_metrics` present, matches pre-fix
  metrics closely — `expected_position_mae` 3.4716 vs 3.4728, consistent with RNG-level
  variation, not a regression).
- Concurrent pair #2 (Bahrain + Australia, both valid this time): the Australia leg was
  interrupted mid-run — see §7, this was the Admiral's worktree sweep killing the process, not
  a reproduction of the deadlock (its CPU/log signature was completely different from the real
  hang: it ran normally for ~90s then vanished with no stall, vs. the real hang's 13-minute flat
  CPU=0). Not counted as evidence either way; flagging so it isn't misread as a recurrence.

**Tests:** full `tests/unit/evo_predictor` + `tests/unit/test_utilization.py` (1972 + supporting
tests): **1978 passed, 19 skipped, 0 failed in 284.07s**, run twice for reproducibility (both
green), foreground (never backgrounded — this environment's background-task-reaping caused a
multi-hour false-hang scare earlier in the run before that was diagnosed and worked around, see
`RESULT_g1-implement.md` "Stop conditions hit"). Independent reviewer re-ran a bounded 123-test
subset in a clean-room dispatch: **123 passed, 0 failed**. Reviewer also ran
`py -m src.utils.simplification_limits` and a Fowler code-smell pass (11/12 clean, 1 logged
override for `duplicated-code` against the `utilization.py` precedent, justified by the
handoff's own scope fence).

## 5. Crew evidence

- Implementer: `RESULT_g1-implement.md` (harvested). Investigated and ruled out a real
  performance-regression concern (single-threaded torch on `test_metalearner.py`'s real MLP
  training + 500-iteration bootstrap CI: no meaningful slowdown, 7.40–9.00s across isolation
  variants). Self-corrected a test-authoring mistake (an `importlib.reload`-based draft broke an
  unrelated test's `is`-identity assertion) before shipping.
- Reviewer: `RESULT_g1-review.md` (harvested). Verdict **APPROVE**, independently reproduced
  worktree identity, ran its own bounded test pass, read the diff line-by-line against the
  `utilization.py` precedent, 0 findings, 0 blockers.

## 6. Triage candidates

- **#632 lives** (flagged in `ADMIRAL_LOG.md` — I independently hit its symptom too): running
  the sampler mutates the per-year DB (`data/f1_data_2024.db` etc. showed as modified, binary
  diff, same size, after full-suite / backtest runs). Not investigated further — out of this
  gate's scope, and the Admiral's log already carries this signal forward to the Phase 0
  scope-checkpoint.
- **Low priority:** `importlib.reload()` of a shared `src/` module inside a test can silently
  break `is`-identity assertions in unrelated, already-imported test modules elsewhere in the
  suite (discovered and self-corrected by the implementer, not shipped, but worth a documented
  lesson for future test authors in this repo).

## 7. End-of-run anomaly — worktree destroyed mid-verification (float to Admiral)

While I was mid-flight on my own second post-fix concurrent-launch verification (g1-integrate's
c3 postcondition — attempting a second, belt-and-suspenders confirmation beyond the first
successful post-fix run), `C:/Programs/f1-623` and the local branch `fix/623-headless-deadlock`
were **deleted out from under me**. My Bash tool's cwd silently resolved to the main checkout
afterward (`git worktree list` now shows only `f1Brainz` and `f1-624`), and one of my two
launched verification processes was killed mid-run without completing (no error, no hang
signature — just vanished after ~90s; not a deadlock recurrence, see §4).

Reading `ADMIRAL_LOG.md` (fresh, timestamped minutes before I discovered this) explains it
fully and legitimately: the Admiral independently ran its own in-regime verification (headless
`sampled-predict` on 2025 Japan, 1000 samples, full 20-driver field, confirmed
`torch.get_num_threads()==1` on the exact forward-pass path that used to deadlock), then
squash-merged PR #633 to main, harvested my worktree's artifacts into
`.agent-work/623-headless-deadlock/` in this checkout, swept the worktree, deleted the branch,
and killed orphan python processes — all while I was still actively driving my own
commander-delegated spine at the `g1-integrate` step, with no handoff signal to me first.

**Consequence for my own spine:** `.agent-work/623-headless-deadlock/spine.json` (harvested,
readable) shows `execute` still `in-progress` at gate `g1-integrate` (postconditions
`c1`/`c2`/`c3` unattested) and `reconcile`/`triage`/`review`/`feedback`/`archive` all still
`pending`. I cannot complete `g1-integrate`'s command-check postcondition as authored (`cd
/c/Programs/f1-623 && py -m pytest ...`) — that directory no longer exists — and re-running
tests against the main checkout directly is both redundant (the Admiral already verified the
merged code in-regime, more rigorously than my own gate required) and outside this launch
order's worktree-only fence for active work. I am **not** fabricating a pass against a
nonexistent path, and I am **not** unilaterally waiving my own postconditions with my own
authority for a decision this consequential.

**Floating to the Admiral:** the underlying deliverable is objectively complete, verified three
independent ways (my crew's tests + independent reviewer + your own in-regime headless
verification), merged, and the issue is closed — so I believe no further engineering work is
needed here. What I cannot decide for myself is how my own spine's bookkeeping should be closed
given its physical prerequisite (the worktree) was removed by your action before I reached
`archive`: (a) treat the epic-level merge + harvest as the terminal closure and let my spine
stand as a superseded/abandoned artifact (harmless — it's already captured, non-authoritative
once main has the merge), or (b) have me provision a fresh minimal worktree solely to formally
waive/advance the remaining spine steps for audit completeness. I'd recommend (a) — rebuilding a
worktree purely to close paperwork on already-shipped, already-verified work seems like the
wrong use of further compute — but this is your call, not mine, since it's your action that
created the state.

## 8. Return status

Deliverable shipped and closed (PR #633, merged, `main` at `16c314b9`). This verdict is the
retroactive audit record from Ship A's side. Standing by for your ruling on §7; not blocking on
it — no further action needed from me unless you want the worktree rebuilt for paperwork
closure.
