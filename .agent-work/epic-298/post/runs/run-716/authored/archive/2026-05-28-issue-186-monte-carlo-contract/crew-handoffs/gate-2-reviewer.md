# Crew Handoff

## Role
`reviewer`

## Assigned Gate
`Gate 2: Sampled Runtime FinalOrderSampleSet v2 And Stage Snapshots`

## Suggested Model Tier
`stronger broad/ambiguous, because runtime contracts and diagnostics touch multiple evo tests`

## Test Mode
`review required; rerun required commands if feasible`

## Task
Review the Gate 2 implementation. Verify `FinalOrderSampleSet` v2, `StageSnapshot` validation, serialization, sampled-runtime population, direct caller updates, scope compliance, and evidence. Return `APPROVE`, `BLOCK`, or `COMMENT`.

## Intent Protected
Probability metadata and traceability stay on the evo runtime side. Strategy remains untouched by Gate 2 and consumes only adapter output from Gate 1.

## Close Criteria
- `FinalOrderSampleSet` has required `schema_version` with current value `2`.
- `StageSnapshot` is typed and validates position distribution, pairwise matrix, ESS, position-distribution stability, and pairwise flip rate.
- `stage_snapshots: dict[str, StageSnapshot]` exists on `FinalOrderSampleSet`; top-level and stage snapshot invariants are tested.
- `stage_diagnostics` remains an opaque provenance dict.
- Serialization emits `schema_version` and `stage_snapshots` as JSON-native values.
- Sampled runtime populates snapshots for `quali`, `race_start`, and `race`.
- Direct evo callers/tests are green.

## Authority
Pilot dispatch after Gate 2 implementer evidence and revised scope. User requested implement everything now.

## Allowed Scope
Review only. You may run commands and inspect diffs. Do not edit files unless a tiny review-note artifact is needed; prefer returning findings.

## Specific Exclusions
Do not implement Gate 3. Do not update docs. Do not edit strategy files. Do not commit, push, PR, or close the issue.

## Relevant Project Rules For This Gate
- Reviewer must check handoff compliance, quality, blockers, and evidence.
- Required verification skipped is a blocker unless justified.
- New/changed interfaces must be clear at call boundary.
- Silent fallback or invalid input continuation is a defect.
- Analysis/model behavior must not drift silently.

## Required Context
- `.agent-work/issue-186-monte-carlo-contract/GATED_PLAN.md`
- `.agent-work/issue-186-monte-carlo-contract/crew-handoffs/gate-2-implementer.md`
- `.agent-work/issue-186-monte-carlo-contract/evidence/gate-2-implementation.md`
- `.agent-work/issue-186-monte-carlo-contract/evidence/gate-2-implementation-fix.md`
- `docs/agents/CREW_CONTEXT.md`
- Current git diff for Gate 2 files.

## Project Mechanics For This Gate
Review only. Do not commit, push, PR, or close the issue. You are not alone in the codebase; do not revert edits made by others.

## Required Evidence
Review verdict with blockers or approval, handoff compliance notes, tests/commands run, and residual risk.

## Required Verification Commands

```bash
py -m pytest tests/unit/evo_predictor/test_runtime_contracts.py tests/unit/evo_predictor/test_sample_state_adapter.py tests/unit/evo_predictor/test_sampled_runtime.py tests/unit/evo_predictor/test_sampled_runtime_serialization.py -v
py -m pytest tests/unit/evo_predictor/test_sampled_backtest.py tests/unit/evo_predictor/test_sampled_predict_cli.py -v
```

## No-Test-Surface Rationale
Not applicable.

## Stop Conditions
Stop and return if evidence cannot be produced, implementation touched out-of-scope areas with behavioral impact, or a blocker requires Pilot/user decision.

## Return Format
`APPROVE | BLOCK | COMMENT`, findings ordered by severity with file/line references, evidence commands, scope concerns, residual risk.
