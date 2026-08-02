# Crew Handoff

## Role
`implementer`

## Assigned Gate
`Gate 2: Sampled Runtime FinalOrderSampleSet v2 And Stage Snapshots`

## Suggested Model Tier
`stronger broad/ambiguous, because runtime contracts and diagnostics touch multiple evo tests`

## Test Mode
`TDD required`

## Task
Add sampled-runtime production result versioning and typed per-stage traceability snapshots. `FinalOrderSampleSet` must become schema v2, include `stage_snapshots: dict[str, StageSnapshot]`, preserve `stage_diagnostics` as opaque provenance, and serialize the new fields as JSON-native values.

## Intent Protected
Probability metadata and traceability stay on the evo runtime side. Strategy continues to consume only its adapter output and must not be touched in this gate.

## Close Criteria
- `FinalOrderSampleSet` has required `schema_version` with current value `2`.
- `StageSnapshot` is typed and validates position distribution, pairwise matrix, ESS, position-distribution stability, and pairwise flip rate.
- `stage_snapshots: dict[str, StageSnapshot]` exists on `FinalOrderSampleSet`; top-level and stage snapshot invariants are tested.
- `stage_diagnostics` remains an opaque provenance dict.
- Serialization emits `schema_version` and `stage_snapshots` as JSON-native values.
- Sampled runtime populates snapshots for `quali`, `race_start`, and `race` from available ordering samples.

## Authority
User answered: implement everything now. Issue comments decide `schema_version`, `StageSnapshot`, and diagnostics split.

## Allowed Scope
`src/evo_predictor/runtime_contracts.py`, `src/evo_predictor/sample_state_adapter.py`, `src/evo_predictor/sampled_runtime.py`, `src/evo_predictor/sampled_runtime_serialization.py`, direct `FinalOrderSampleSet` callers in `src/evo_predictor/sampled_backtest.py` and `src/evo_predictor/run.py` if required by tests, related tests under `tests/unit/evo_predictor`.

## Specific Exclusions
Do not change sampling math or module training behavior. Do not add DNF/DNS sampled status fields. Do not emit bulky new committed artifacts. Do not edit strategy files or docs in this gate.

## Relevant Project Rules For This Gate
- TDD for logic changes.
- Strict validation with field names, expectation, and actual values.
- One canonical representation per boundary.
- No silent fallbacks.
- Use `py`, not `python`.

## Required Context
- `.agent-work/issue-186-monte-carlo-contract/GATED_PLAN.md`
- `.agent-work/issue-186-monte-carlo-contract/PROBLEM_INTERROGATION_RESULT.md`
- `docs/agents/CREW_CONTEXT.md`
- `src/evo_predictor/runtime_contracts.py`
- `src/evo_predictor/sample_state_adapter.py`
- `src/evo_predictor/sampled_runtime.py`
- `src/evo_predictor/sampled_runtime_serialization.py`

## Project Mechanics For This Gate
Do not commit, push, PR, or close the issue. Edit directly in the current workspace. You are not alone in the codebase; do not revert edits made by others and accommodate existing Gate 1 changes.

## Required Evidence
Diff summary, tests added/updated before implementation, verification command output summary, blockers if any, and explicit statement that sampling/model semantics were not changed.

## Required Verification Commands

```bash
py -m pytest tests/unit/evo_predictor/test_runtime_contracts.py tests/unit/evo_predictor/test_sample_state_adapter.py tests/unit/evo_predictor/test_sampled_runtime.py tests/unit/evo_predictor/test_sampled_runtime_serialization.py -v
py -m pytest tests/unit/evo_predictor/test_sampled_backtest.py tests/unit/evo_predictor/test_sampled_predict_cli.py -v
```

## No-Test-Surface Rationale
Not applicable.

## Stop Conditions
Stop and return if diagnostics formulas require a modeling decision beyond issue comments, runtime snapshots require changing sample generation semantics, allowed scope is exceeded, or evidence cannot be produced.

## Return Format
Diff summary, files changed, tests run with pass/fail result, blockers, scope concerns, assumptions used.
