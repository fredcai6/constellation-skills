# Mission Frame — #623 headless deadlock

Shrunk per template guidance: this is a trivial, local, mechanical fix (one entrypoint file
gains an unconditional thread-cap at import time, mirroring an existing pattern already in the
repo) — the packet map adds context but is not load-bearing for the decision.

## Intent
Make `py -m src.evo_predictor.run sampled-backtest ...` (and by extension `sampled-predict`,
`gold-cycle`) complete headlessly instead of deadlocking at 0% CPU on race 1, by removing the
console-handle-dependent torch native thread-pool init path from the hot loop.

## Affected Capabilities
- `struct:evo` (`src/evo_predictor/`) — CLI entrypoint (`run.py`) only; no change to the sampled
  runtime simulator, field solve, or fusion logic itself.

## Structural Anchors
- `src/evo_predictor/run.py` — CLI entrypoint, module import order; fix lands here.
- `src/evo_predictor/module_runtime.py:194` — `run_module_field`'s
  `loaded.module.predict(pair_batch.batch)`, the first real torch forward pass per process
  lifetime; this is the blocking call, unmodified by this fix (fixed at its cause, not its site).
- `src/utils/utilization.py:203-220` (`init_worker`) — existing precedent: the exact same
  env-var + `torch.set_num_threads` pattern, already applied inside `ProcessPoolExecutor`
  workers. This fix applies the same pattern once, unconditionally, at the CLI entrypoint.

## Governing Constraints / Assumptions
- Canonical Data Constraint (DB-only analysis) — untouched, this fix touches no data path.
- Launch-order Pre-Ruling #3 — bounded fix only; no backtest architecture refactor, no
  production model defaults changed beyond thread/env settings.
- Launch-order Pre-Ruling #2 — fix must be unconditional at the entrypoint, not gated on
  `isatty()`.

## Decision Anchors & Decision Pressure
- No existing decision anchor governs this narrow a fix. No new durable decision anchor is
  proposed — this is a bug fix, not a new capability or interface.

## Claims / Evidence Surfaces
- Existing evo_predictor unit test suite (`tests/unit/evo_predictor/`, notably
  `test_run_cli_defaults.py`, `test_sampled_backtest_runtime.py`, `test_module_runtime.py`)
  must stay green — the fix must not change any CLI argument default or prediction output.
  A new unit test asserts the entrypoint caps torch threads on import.
  The `gN-integrate` gate re-confirms with a real headless 1-race `sampled-backtest` run.

## Map Confidence / Staleness / Disputes
- None — the affected file (`run.py`) carries no packet-level low-confidence flag; the packet
  documents it as the stable CLI entry point.

## Out of Scope
- Any change to `sampled_runtime.py`, `module_runtime.py`, `sampled_backtest.py`, or the
  ProcessPoolExecutor parallel path in `src/utils/utilization.py`.
- Any change to production model defaults, manifest schema, or fantasy-scoring behavior.
- Root-causing exactly *why* Windows' torch thread-pool init blocks under a detached console
  (deep OS/runtime internals) — out of scope once the fix is verified to close the observable
  hang; the mechanism is documented as "most likely," not exhaustively proven at the OS level.

## Plan-alternatives / cold-critic note (design-it-twice, bias-to-yes)
Two candidate fix sites were compared in this context (no parallel subagent dispatch — the
change is genuinely trivial and single-file, so a full alternatives panel is a named untaken
road):
1. **Chosen: cap threads unconditionally at the top of `run.py`**, before any transitive torch
   import. Matches the diagnosis's root-cause claim (lazy native thread-pool init on first
   large forward pass), mirrors the existing `init_worker` precedent, requires touching exactly
   one file, and is unconditional per Pre-Ruling #2.
2. **Rejected: guard inside `module_runtime.run_module_field`** (e.g., a lazy one-time
   `torch.set_num_threads(1)` call before the first `predict()`). Rejected because by the time
   `run_module_field` executes, torch has already been imported and any native thread-pool
   auto-init triggered by an earlier incidental op could already have started; capping at the
   true entrypoint is strictly earlier and cheaper, and avoids adding an import-order-sensitive
   side effect inside a hot-path module whose job is field composition, not runtime config.
A single cold read of this frame + the execute plan (below) stands in for a full critic
dispatch, given the bounded, single-file, precedented nature of the change — flagged as an
untaken road rather than silently skipped.
