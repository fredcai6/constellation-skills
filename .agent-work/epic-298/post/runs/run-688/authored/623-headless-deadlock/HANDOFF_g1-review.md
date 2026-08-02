# Reviewer Handoff

## Gate
g1-review (work-id 623-headless-deadlock, branch fix/623-headless-deadlock, worktree C:/Programs/f1-623)

## What was implemented
Issue #623: `sampled-backtest`/`sampled-predict`/`gold-cycle` deadlocked at 0% CPU on the first
race when launched headless (no controlling console/window-station). Root cause: the first real
PyTorch forward pass in the process's lifetime (`src/evo_predictor/module_runtime.py:194`)
triggers torch's native CPU thread-pool lazy init, whose init path is console-handle-dependent
on Windows. Fix: cap BLAS/OMP env vars and `torch.set_num_threads(1)` unconditionally at the
very top of `src/evo_predictor/run.py`, before any of its project imports run (several
transitively `import torch` at module level). Mirrors the existing precedent in
`src/utils/utilization.py:203-220` (`init_worker`), which does the same thing but only inside
`ProcessPoolExecutor` workers — this fix applies it once, unconditionally, at the CLI
entrypoint.

## How to inspect the diff
```bash
cd /c/Programs/f1-623
git diff src/evo_predictor/run.py
cat tests/unit/evo_predictor/test_run_entrypoint_thread_cap.py
git status --short   # should show only these two files touched (plus .agent-work/, untracked)
```
Full IMPLEMENTER_RESULT (diff, test output, investigation notes) is at
`.agent-work/623-headless-deadlock/RESULT_g1-implement.md`.

## Task statement
Verify the fix is: (1) correct (actually placed before every transitive torch import in
`run.py`, unconditional, guarded so torch-absent environments still import cleanly);
(2) minimal/in-scope (touches only `run.py` + the one new test file, no other production file,
no CLI/behavior change); (3) backed by real, fresh, reproducible evidence (not just claimed).

## Close Criteria
- The inserted block in `run.py` sits after the stdlib imports and before `import numpy as np` /
  the first `from src....` import — i.e. genuinely before any transitive torch import can occur.
- The four env vars use `os.environ.setdefault` (respects an operator override); `torch.set_num_threads(1)`
  itself is unconditional (not behind an `isatty()` or similar check) per LAUNCH_ORDER Pre-Ruling #2.
- The `import torch` + `torch.set_num_threads(1)` pair is wrapped in a broad guarded
  try/except so `run.py` still imports cleanly if torch is absent (mirrors
  `src/utils/utilization.py:init_worker`'s pattern — check that file for the convention).
- The new test file asserts `torch.get_num_threads() == 1` after importing `src.evo_predictor.run`,
  and that the four env vars are present in `os.environ`.
- No other production file changed (`module_runtime.py`, `sampled_runtime.py`,
  `sampled_backtest.py`, `sampled_backtest_scoring.py`, `src/utils/utilization.py` all untouched).
- No CLI argument/default changed — spot-check `git diff` shows nothing outside the thread-cap
  block.

## Allowed Scope (for this review)
Read/run only — you may re-run tests and inspect files, but do not edit `run.py`, the test file,
or any other production code. If you find a real defect, return BLOCK with the specific finding;
do not fix it yourself.

## Specific Exclusions
None beyond standard reviewer read-only posture.

## Constraints
- Verify the claimed evidence yourself, don't take IMPLEMENTER_RESULT's word for it: re-run at
  least the new test file and confirm the worktree-identity check
  (`py -c "import src.evo_predictor.run as r; print(r.__file__)"` must print a path under
  `C:\Programs\f1-623`, not the main checkout) before trusting any test output.
- **Do NOT re-run the full `tests/unit/evo_predictor` directory (1972 tests) — it is legitimate
  but takes ~5 minutes in the foreground and this environment's background-task-reaping has
  caused multi-hour false-hang confusion when backgrounded (see IMPLEMENTER_RESULT's "Stop
  conditions hit" section and this repo's lesson "harness reaps long bg tasks + orphans
  children"). Run the bounded set below instead — it is sufficient to independently confirm the
  fix and reuses the implementer's already-diagnosed regime. If you need more coverage, extend
  this list modestly, but always run pytest commands in the FOREGROUND (not `run_in_background`,
  not piped through `tail`, not `nohup &`), and budget under 2 minutes.**

```bash
cd /c/Programs/f1-623
py -c "import src.evo_predictor.run as r; print(r.__file__)"
py -m pytest tests/unit/evo_predictor/test_run_entrypoint_thread_cap.py tests/unit/evo_predictor/test_run_cli_defaults.py tests/unit/evo_predictor/test_module_runtime.py tests/unit/evo_predictor/test_sampled_backtest_runtime.py tests/unit/evo_predictor/test_sampled_runtime.py tests/unit/test_utilization.py -q
```

## Map Anchors (inbound)
Same as g1-implement's anchors block in execute.json:
- **Structural:** `src/evo_predictor/run.py`; `src/utils/utilization.py:203-220`.
- **Capability:** `struct:evo` — CLI entrypoint only.
- **Constraints:** LAUNCH_ORDER Pre-Ruling #2 (unconditional), Pre-Ruling #3 (bounded fix).
- **Evidence expectations:** evo_predictor + utilization unit suites stay green.

## Evidence from IMPLEMENTER_RESULT
- Full diff of `run.py` (23 lines added, nothing removed).
- New test file content (2 tests).
- Full-suite evidence: `1978 passed, 19 skipped, 0 failed in 284.07s` (run twice, foreground).
- Bounded-set evidence: `123 passed in 41.41s`.
- Worktree-identity check confirmed `C:\Programs\f1-623\src\evo_predictor\run.py`.
- Investigated and ruled out a performance-regression stop condition (single-threaded torch on
  `test_metalearner.py`'s real MLP training: no meaningful slowdown, 8.22s vs 7.40s/9.00s across
  isolation variants).
- Self-corrected a test-authoring mistake (an early `importlib.reload`-based test draft broke an
  unrelated test's `is`-identity assertion) before it shipped — final test uses plain import.
- Reverted an out-of-scope side effect (4 DB fixture files dirtied by the full suite run) via
  `git checkout --` before returning.

## Verification Commands
See "Constraints" above — the bounded command block is the required verification; run it
yourself, don't just read the pasted output.

## Suggested Model Tier
Simple bounded.

## Authority
The fix approach itself is not open for re-litigation (already decided by the launch order) —
review is for correctness/scope/evidence-integrity, not second-guessing the chosen mechanism.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE/BLOCK), what you independently verified (with your own
command output), any findings, workflow feedback.
