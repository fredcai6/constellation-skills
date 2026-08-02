# Review Result

## Assigned Gate
`g1-review` (work-id 623-headless-deadlock, branch fix/623-headless-deadlock, worktree C:/Programs/f1-623)

## Result
`APPROVE`

Survey driven end-to-end through the checklist engine at
`.agent-work/623-headless-deadlock/g1-review/review.json` (session `ShipA-623-g1review`, lease
claimed then released). All 7 items (r0-context, r1-handoff, r2-scope, r3-evidence, r4-quality,
r5-reconciliation, r6-fowler) recorded `pass`; consolidated `APPROVE`, 0 findings, 0 blockers.

## Handoff compliance
Fix does what the handoff asked, within its allowed scope. Read `src/evo_predictor/run.py` directly
(not just the diff): the inserted block (lines 17-38) sits after all stdlib imports (`os`, `sys`,
`logging`, etc., lines 6-15) and before `import numpy as np` (line 40) and every `from src....`
import — genuinely before any transitive `import torch` can fire. Four env vars
(`OMP_NUM_THREADS`, `MKL_NUM_THREADS`, `OPENBLAS_NUM_THREADS`, `NUMEXPR_NUM_THREADS`) use
`os.environ.setdefault(...)`. `torch.set_num_threads(1)` is unconditional — no `isatty()` or
similar gate. The `import torch` + `torch.set_num_threads(1)` pair is wrapped in a broad
`try/except Exception` with a `logging.getLogger(__name__).debug(...)` fallback, structurally
identical to `src/utils/utilization.py:203-224` (`init_worker`) — read both side by side to
confirm. New test file `tests/unit/evo_predictor/test_run_entrypoint_thread_cap.py` asserts
`torch.get_num_threads() == 1` and that all 4 env vars are present in `os.environ` after import.

## Scope drift
None. `git status --short` and `git diff --stat` (both run myself, not read from the
implementer's report) confirm exactly one production file changed
(`src/evo_predictor/run.py`, +23/-0) and one new test file added
(`tests/unit/evo_predictor/test_run_entrypoint_thread_cap.py`), plus the untracked
`.agent-work/` scratch dir. `module_runtime.py`, `sampled_runtime.py`, `sampled_backtest.py`,
`sampled_backtest_scoring.py`, and `src/utils/utilization.py` are all untouched. No CLI
argument/default changed anywhere in the diff — it is purely additive.

## Evidence verdict
Independently reproduced, not taken on the implementer's word:
- Worktree identity: `py -c "import src.evo_predictor.run as r; print(r.__file__)"` printed
  `C:\Programs\f1-623\src\evo_predictor\run.py` — confirmed running against the worktree, not
  the main checkout (editable-install `.pth` trap avoided).
- Bounded test set (exact command from the handoff), run in the foreground:
  ```
  py -m pytest tests/unit/evo_predictor/test_run_entrypoint_thread_cap.py tests/unit/evo_predictor/test_run_cli_defaults.py tests/unit/evo_predictor/test_module_runtime.py tests/unit/evo_predictor/test_sampled_backtest_runtime.py tests/unit/evo_predictor/test_sampled_runtime.py tests/unit/test_utilization.py -q
  ```
  Result: **123 passed, 0 failed, 0 errors, in 111.78s** (pytest-reported wall time, under the
  handoff's 2-minute test-time budget). Test count matches the implementer's claimed 123 exactly;
  duration differs from the claimed 41.41s (likely machine load / cold cache at review time) but
  does not affect the pass/fail verdict.
  - Process note for the record: the harness's own 120s tool-call timeout auto-backgrounded this
    command mid-run (task id `bb043axn7`) despite it being issued as a plain blocking Bash call.
    Per this run's doctrine (`global-everyone.md` "never end your turn to wait"), I did not end
    my turn — I polled the background output file in a 5s loop inside the same turn until the
    `passed`/`failed` summary line appeared (landed on the first check), then read the full tail.
    This is not the multi-hour false-hang the handoff warned about (that was triggered by
    deliberately backgrounding/piping the full 1972-test directory); this was the harness's
    generic per-call timeout on an ordinary bounded command, recovered by active polling within
    the same turn as instructed.
  - `git status --short` after the run showed no new dirtied files — no repeat of the DB-fixture
    side effect the implementer noted from the full-suite run (expected: this bounded set does
    not touch DB fixtures).
- Also ran the project-mandated `py -m src.utils.simplification_limits --paths
  src/evo_predictor/run.py tests/unit/evo_predictor/test_run_entrypoint_thread_cap.py` (CREW_CONTEXT
  "Simplification limits" review-blocker rule) → `PASS (2 files checked)`.

## Code/doc quality
Minimal, matches surrounding conventions, guarded so torch-absent environments still import
cleanly (verified: the except branch never re-raises). Comment block (lines 17-24) explains the
Windows-specific root cause and issue reference — earns its length, does not compensate for
unclear code. No hidden fallback: the guard is a documented, logged exception path, not a silent
swallow (fail-visibly posture from `global-crew.md` honored). See "Refactoring pass" below for the
one judgment call (duplicated-code, overridden).

### Refactoring pass (Fowler code smells)
Recorded to `.agent-work/623-headless-deadlock/g1-review/fowler_pass.json`, verified by
`scripts/verify_fowler_pass.py` → **exit 0**, `smells=12, flagged=[], overridden=['duplicated-code']`.

- 11/12 baseline smells: **absent** (long-method, large-class, feature-envy, data-clumps,
  primitive-obsession, long-parameter-list, shotgun-surgery, divergent-change, message-chains,
  speculative-generality, comments-as-deodorant).
- **duplicated-code: overridden.** The new setdefault-loop + guarded-torch-import block in
  `run.py` structurally near-duplicates `src/utils/utilization.py:203-224` (`init_worker`) — same
  4-var tuple, same try/import-torch/except-Exception/debug-log shape (~15-20 lines). Logged
  override: the handoff's Close Criteria explicitly forbid touching `utilization.py` in this gate,
  and its Authority section forbids re-litigating the chosen mechanism — extracting a shared
  helper is out of scope for this bounded fix. The duplication is also not exact: `run.py` uses
  `setdefault` (respects an operator's explicit override at the entrypoint) vs `utilization.py`'s
  direct assignment (enforces an exact per-worker thread count), so a shared helper would need a
  parameter to express that divergence anyway.

## Map impact verdict
Handoff's Map Anchors (`struct:evo` — CLI entrypoint only; `src/evo_predictor/run.py`,
`src/utils/utilization.py:203-220` as precedent) match the diff exactly. No new
structural/capability/constraint impact beyond the named entrypoint — evidence supports the
claimed change, constraints (Pre-Ruling #2 unconditional, Pre-Ruling #3 bounded) were honored, no
decision candidate was needed, nothing durable to route to Cartographer or Triage.

## Reconciliation check
None. This is a same-pattern extension of an already-recorded precedent
(`utilization.py:init_worker`) applied at one additional seam, not a new pattern or module
boundary. No new dependency, no new public interface, no schema/contract change.

## Blockers
- none

## Out-of-scope observations
- none

## Workflow Feedback

- **Handoff gaps:** none — confirmed after review: the handoff's bounded test-command block,
  close criteria, and evidence expectations were all directly actionable with no field missing or
  ambiguous.
- **Context rediscovered:** none beyond what the handoff already pointed at
  (`src/utils/utilization.py:203-220` as the mirrored convention) — reading that file side-by-side
  with the diff was sufficient.
- **Instructions improvised around:** the handoff says "run it in the FOREGROUND (a plain
  blocking Bash call, not `run_in_background`, not piped through `tail`, not `nohup`)" — I did
  exactly that, but the harness's own per-tool-call 120s timeout still auto-moved the command to
  background mid-run (this is a harness behavior, not something the caller's command shape
  controls). The handoff's stop-condition framing is specifically about *deliberately*
  backgrounding/piping the full 1972-test suite; it doesn't cover a plain foreground call getting
  silently auto-backgrounded by the tool's own timeout. I treated this the same way per the
  inherited `global-everyone.md` "never end your turn to wait" doctrine — polled the output file
  in-turn until the result landed — which worked cleanly (first poll, ~5s). Worth a one-line
  addendum in future handoffs of this shape: "if the harness auto-backgrounds the bounded command
  anyway, poll in-turn rather than treating it as the same failure mode as the full-suite hang."
- **What would have made this easier:** nothing material — the handoff was unusually
  well-scoped and the bounded command was correctly sized (123 tests, ~2 min).

## Return status
`complete`
