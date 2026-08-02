# Gated Plan: `issue-256-oracle-state-sampled-backtest`

## Problem Statement

Sampled runtime backtesting has only the baseline sampled-state path. Issue 256 requires optional oracle-state modes that replace sampled grid and/or lap-N handoff state with DB truth so backtest error can be attributed to quali/grid sampling, race-start sampling, and race-power/fusion stages.

## Intent Protected

Backtest modes must be explicit, validated, DB-only, and diagnostically clear. Missing oracle data must not silently fall back to sampled state.

## Scope

**Allowed regions/files:** `src/evo_predictor/sampled_runtime.py`, `src/evo_predictor/sampled_backtest.py`, `src/evo_predictor/run.py`, sampled runtime serialization if needed, focused evo tests, focused evo docs.  
**Not scope:** `sampled-predict`, training pipelines, manifest schema changes, data ingestion, artifact regeneration, gold promotion.  
**Specific exclusions:** `No FastF1 calls; no dead-path updates; no new external data source.`

## Structural Baseline

**Need:** `yes`  
**Status:** `established`  
**Evidence:** `docs/architecture/index.md` places sampled runtime under struct:evo and confirms DB-only data access through SQLite; relevant code in src/evo_predictor/sampled_runtime.py and sampled_backtest.py.`

## Authority / Assumptions

- `User invoked constellation-pilot issue 256.`
- `Orchestrator permits local branch/artifacts/code edits; ask before push, PR, merge, or issue close.`
- `oracle_grid = DB Q classification.`
- `oracle_lap_n = DB race_start_order for runtime race_start_target_lap.`
- `Missing oracle input is an explicit per-event skip with diagnostics.`

## Test Mode

**Plan default:** `TDD required; full evo unit suite required after focused tests.`  
**Inspection-only rationale:** `not applicable`

## Project Mechanics Hooks

| Moment | Hook | Owner | Evidence |
|---|---|---|---|
| Before gate | `branch` | `Pilot` | `codex/issue-256-oracle-state-sampled-backtest` |
| After gate evidence accepted | `commit optional` | `Pilot` | `not requested yet` |
| Before closeout | `archive workflow artifacts optional` | `Pilot` | `skip unless user asks` |
| After archive | `push/PR/close ask first` | `Pilot` | `Orchestrator requires approval` |

## Gates

### Gate 1: `oracle-state sampled backtest modes`

**Purpose:** `Add the four issue modes and observable diagnostics in one cohesive evo behavior slice.`  
**Crew cycle:** `implementer Crew -> integrate evidence -> reviewer Crew -> integrate evidence -> gate close`  
**Implementer handoff:** `required`  
**Reviewer handoff:** `required`  
**Suggested model tier:** `simple bounded, because scope is localized but correctness-sensitive`  
**Test mode:** `TDD required`  
**Allowed scope:** `src/evo_predictor/sampled_runtime.py`, `src/evo_predictor/sampled_backtest.py`, `src/evo_predictor/run.py`, `tests/unit/evo_predictor/test_sampled_backtest.py`, `tests/unit/evo_predictor/test_sampled_backtest_cli.py`, focused docs under docs/evo or src/evo_predictor/README.md`  
**Specific exclusions:** `No sampled-predict mode flag; no manifest schema change; no data ingestion change.`

**Close criteria:**
- [x] `backtest_sampled_runtime` validates and reports the selected mode.
- [x] `sampled-backtest --mode` accepts exactly `sampled_state`, `oracle_grid`, `oracle_lap_n`, `oracle_all_states`.
- [x] Oracle grid and lap-N inputs are applied before the downstream stage they are meant to isolate.
- [x] Missing oracle state skips the event with explicit diagnostics.
- [x] Docs mention the new mode flag and semantics.

**Required evidence:**
- `py -m pytest tests/unit/evo_predictor/test_sampled_backtest.py tests/unit/evo_predictor/test_sampled_backtest_cli.py -v`
- `py -m pytest tests/unit/evo_predictor -v`
- `diff inspection for DB-only access and no silent fallback`

**Stop conditions:** `Mode semantics require a user decision; oracle data cannot be sourced from existing DB APIs; scope expands outside evo sampled runtime/backtest.`  
**Next gate:** `closeout`

## Triage Candidate Log

| Candidate | Reason | Anchor | Evidence | Status |
|---|---|---|---|---|

## Plan-Level Stop Conditions

- unresolved human decision affects scope, authority, or evidence
- required evidence cannot be produced
- scope expands beyond allowed regions/files
- specific exclusion must be touched
- structural uncertainty affects ownership, dependency, scope, or evidence

## Final Completion Criteria

- [x] all gates closed or remaining blockers listed
- [x] each implementation gate completed its Crew cycle
- [x] evidence satisfies close criteria
- [x] assumptions still hold
- [x] architecture reconciliation checked
- [x] Triage candidates routed, dropped because `reason`, or none
