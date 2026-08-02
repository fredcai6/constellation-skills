# Crew Handoff

## Role
`reviewer`

## Assigned Gate
`Gate 1: oracle-state sampled backtest modes`

## Suggested Model Tier
`simple bounded, because review scope is localized but correctness-sensitive`

## Test Mode
`review evidence required`

## Task
Review the implementation for issue 256 oracle-state sampled backtest modes. Do not edit files unless a small blocking fix is necessary and clearly within scope; prefer returning findings.

## Intent Protected
Backtest modes must be explicit, validated, DB-only, diagnostically clear, and must not silently fall back when oracle state is missing.

## Close Criteria
Reviewer confirms or blocks that the implementation satisfies the gate: exact modes, CLI validation, oracle state at correct handoff boundaries, missing oracle state skips explicitly, docs updated, focused and full evo tests credible.

## Authority
`Pilot reviewer handoff for issue 256`

## Allowed Scope
Review only these changed files unless a direct dependency must be inspected: `src/evo_predictor/sampled_runtime.py`, `src/evo_predictor/sampled_backtest.py`, `src/evo_predictor/run.py`, `tests/unit/evo_predictor/test_sampled_backtest.py`, `tests/unit/evo_predictor/test_sampled_backtest_cli.py`, `src/evo_predictor/README.md`, `.agent-work/issue-256-oracle-state-sampled-backtest/GATED_PLAN.md`.

## Specific Exclusions
Do not touch `.agent-work/issue-261-loso-fusion/`. Do not request broad refactors, manifest schema changes, data ingestion changes, sampled-predict CLI changes, or artifact regeneration unless they are necessary to prevent a correctness bug.

## Relevant Project Rules For This Gate
- Analysis code must read from SQLite DB only.
- No silent fallback on missing data for oracle modes.
- Public/meaningful boundaries need strict validated inputs and descriptive failures.
- Tests must cover behavior, not just parser shape.
- Reviewer approval alone is insufficient; include evidence reviewed.

## Required Context
- `.agent-work/issue-256-oracle-state-sampled-backtest/GATED_PLAN.md`
- Current diff for the changed files
- Implementer evidence in subagent notification

## Project Mechanics For This Gate
`do not commit; return review evidence to Pilot`

## Required Evidence
List findings ordered by severity with file/line references. If no findings, say so and mention any residual risks or test gaps. Confirm whether focused and full evo unit evidence is sufficient.

## Required Verification Commands
Optional rerun if needed. If not rerun, state review is based on diff inspection and implementer evidence.

## No-Test-Surface Rationale
`not applicable`

## Stop Conditions
Stop and return if a blocking issue is found, scope exceeds handoff, or evidence is insufficient.

## Return Format
`findings, evidence reviewed, blocker status, residual risk/test gaps`
