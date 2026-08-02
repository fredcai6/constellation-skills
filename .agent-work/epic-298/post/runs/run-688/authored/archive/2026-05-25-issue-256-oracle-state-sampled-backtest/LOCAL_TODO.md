# Local Work Todo: `issue-256-oracle-state-sampled-backtest`

## Task summary

Add oracle-state modes to sampled runtime backtesting for GitHub issue 256, preserving DB-only inputs, strict mode validation, explicit failure on missing oracle state, and evo-region test evidence.

## Source context

**Work ID:** `issue-256-oracle-state-sampled-backtest`  
**Role:** `pilot`  
**Route/gate:** `Gate 1: oracle-state sampled backtest modes`  
**Handoff/framing source:** `GitHub issue 256`  
**Authority:** `user invoked constellation-pilot for issue 256; Orchestrator permits branch/artifacts/code edits autonomously`

## Definition of done

- [ ] `sampled-backtest` accepts `sampled_state`, `oracle_grid`, `oracle_lap_n`, and `oracle_all_states`.
- [ ] Oracle modes use only DB `Q` classification and `race_start_order` state, with no silent fallback.
- [ ] Tests are written first and evo-region verification is run.
- [ ] Docs are updated where sampled runtime backtest behavior is described.

## Todo

- [x] Load project and issue context.
- [x] Bound scope and create Pilot artifacts.
- [x] Dispatch implementation Crew and integrate evidence.
- [x] Dispatch reviewer Crew and integrate evidence.
- [x] Reconcile architecture/docs and close out.

## Work log

### Step 1: `context and scope`

**Status:** `completed`  
**What happened:** Loaded repo guidance, issue 256, sampled runtime/backtest code, and current tests.  
**Evidence:** `docs/agents/ORCHESTRATOR_CONTEXT.md`, `docs/agents/CREW_CONTEXT.md`, `src/evo_predictor/sampled_runtime.py`, `src/evo_predictor/sampled_backtest.py`, `tests/unit/evo_predictor/test_sampled_backtest.py`  
**Follow-up:** Dispatch implementation gate.

### Step 2: `implementation and review`

**Status:** `completed`  
**What happened:** Implementer Crew added oracle-state modes, CLI flag, diagnostics, docs, and tests. Reviewer Crew approved with no blockers. Pilot added a direct runtime oracle-handoff regression test.  
**Evidence:** `py -m pytest tests\unit\evo_predictor\test_sampled_runtime.py tests\unit\evo_predictor\test_sampled_backtest.py tests\unit\evo_predictor\test_sampled_backtest_cli.py -v` -> `48 passed`; `py -m pytest tests\unit\evo_predictor -v` -> `911 passed, 69 warnings`  
**Follow-up:** none

## Current state

**Last completed step:** `implementation and review`  
**Current blocker:** `none`  
**Next recommended action:** `final report to user`  
**Files/artifacts touched:** `src/evo_predictor/sampled_runtime.py`, `src/evo_predictor/sampled_backtest.py`, `src/evo_predictor/run.py`, `tests/unit/evo_predictor/test_sampled_runtime.py`, `tests/unit/evo_predictor/test_sampled_backtest.py`, `tests/unit/evo_predictor/test_sampled_backtest_cli.py`, `src/evo_predictor/README.md`, `.agent-work/issue-256-oracle-state-sampled-backtest/`  
**Open assumptions:** `oracle_grid uses DB Q classification; oracle_lap_n uses DB race_start_order for runtime race_start_target_lap`
