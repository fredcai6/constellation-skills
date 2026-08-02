# Evidence Integration

## Gate
`Gate 2: Sampled Runtime FinalOrderSampleSet v2 And Stage Snapshots`

## Crew Result

**Role:** `implementer`  
**Status:** `partial`

## Implementation Evidence
- Added `StageSnapshot` and `FinalOrderSampleSet` schema v2 validation.
- Added required `stage_snapshots` on `FinalOrderSampleSet`.
- Added JSON serialization for `schema_version` and `stage_snapshots`.
- Added snapshot construction from existing ordering samples.
- Updated sampled runtime to populate snapshots for `quali`, `race_start`, and `race`.
- Required original Gate 2 command: `54 passed`.
- Extra caller check failed: `tests/unit/evo_predictor/test_sampled_backtest.py tests/unit/evo_predictor/test_sampled_predict_cli.py -v` -> `19 failed, 9 passed`.

## Review Evidence
`not dispatched yet`

## Required Evidence Check
`missing: direct evo callers still fail under new required contract`

## Verification Command Check
`original required command passed; expanded direct-caller command failed`

## Original Intent Check
`concern: required contract is not yet integrated across direct evo callers`

## Scope Drift Check
`scope needed revision: direct FinalOrderSampleSet callers were omitted from Gate 2 allowlist`

## Assumption Check
`traceability diagnostics are non-model behavior; still holds`

## Reviewer Approval Check
`not applicable yet`

## New Information
- `src/evo_predictor/sampled_backtest.py` directly constructs `FinalOrderSampleSet` and must be updated in Gate 2.
- `tests/unit/evo_predictor/test_sampled_predict_cli.py` constructs fixtures that must include `stage_snapshots`.

## Architecture Reconciliation Implication
`no action`

## Pilot Decision
`revise gated plan and send back to Crew`

## Reason
A required `FinalOrderSampleSet` constructor change must leave direct evo callers green before review.

## Plan / Checklist Updates Required
- Expand Gate 2 allowed scope and required verification commands.
- Send implementer a narrow follow-up.
