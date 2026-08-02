# Crew Handoff

## Role
`implementer`

## Assigned Gate
`Gate 1: oracle-state sampled backtest modes`

## Suggested Model Tier
`simple bounded, because scope is localized but correctness-sensitive`

## Test Mode
`TDD required`

## Task
Add issue 256 oracle-state modes to sampled runtime backtesting.

## Intent Protected
Backtest modes must be explicit, validated, DB-only, diagnostically clear, and must not silently fall back when oracle state is missing.

## Close Criteria
`sampled-backtest` accepts and wires `sampled_state`, `oracle_grid`, `oracle_lap_n`, and `oracle_all_states`; backtest diagnostics record selected/available modes; oracle grid/lap-N state is used at the correct handoff boundaries; missing oracle state produces explicit per-event skip diagnostics; focused docs are updated.

## Authority
`GitHub issue 256; Pilot assumptions recorded in GATED_PLAN.md`

## Allowed Scope
`src/evo_predictor/sampled_runtime.py`, `src/evo_predictor/sampled_backtest.py`, `src/evo_predictor/run.py`, `tests/unit/evo_predictor/test_sampled_backtest.py`, `tests/unit/evo_predictor/test_sampled_backtest_cli.py`, focused docs under `docs/evo/` or `src/evo_predictor/README.md`.

## Specific Exclusions
No sampled-predict mode flag; no manifest schema change; no data ingestion change; no FastF1 or external data access; do not touch unrelated files or the existing `.agent-work/issue-261-loso-fusion/`.

## Relevant Project Rules For This Gate
- Use `py`, not `python`.
- TDD for logic changes.
- Evo code must read analysis state from the SQLite DB only.
- Validate public boundary inputs with descriptive exceptions.
- Run full evo unit suite before declaring complete.

## Required Context
- `.agent-work/issue-256-oracle-state-sampled-backtest/GATED_PLAN.md`
- `src/evo_predictor/sampled_runtime.py`
- `src/evo_predictor/sampled_backtest.py`
- `src/evo_predictor/sample_state_adapter.py`
- `tests/unit/evo_predictor/test_sampled_backtest.py`
- `tests/unit/evo_predictor/test_sampled_backtest_cli.py`

## Project Mechanics For This Gate
`do not commit; return evidence to Pilot`

## Required Evidence
Tests failing first for the new mode behavior, then passing after implementation; focused and full evo unit test commands; diff summary.

## Required Verification Commands
`py -m pytest tests/unit/evo_predictor/test_sampled_backtest.py tests/unit/evo_predictor/test_sampled_backtest_cli.py -v`
`py -m pytest tests/unit/evo_predictor -v`

## No-Test-Surface Rationale
`not applicable`

## Stop Conditions
Stop and return if allowed scope is exceeded, a specific exclusion must be touched, evidence cannot be produced, hidden intent would need inference, or an authority/dependency/failure policy decision is needed.

## Return Format
`diff summary, evidence, blockers, scope concerns, assumptions used`
