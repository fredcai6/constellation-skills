# Crew Handoff

## Role
`reviewer`

## Assigned Gate
`Gate 1: Strategy ClassificationFutureSet v2`

## Suggested Model Tier
`simple bounded, because implementation is localized but fixture/report churn is broad`

## Test Mode
`review required; rerun required focused command if feasible`

## Task
Review the Gate 1 implementation. Verify handoff compliance, scope, strict v2 validation, removal of truncation semantics, strategy/evo boundary, and required evidence. Return `APPROVE`, `BLOCK`, or `COMMENT`.

## Intent Protected
Strategy/fantasy consumes only the narrow strategy contract and does not import evo runtime internals. Runtime production semantics remain outside strategy.

## Close Criteria
- Gate 1 close criteria in `GATED_PLAN.md` are satisfied or blockers are identified.
- No strategy direct import of evo internals.
- No `max_futures` compatibility path remains in Gate 1 source/report CLI.
- v2 integer index futures are validated and serialized clearly.
- Fixture generator change is either accepted as directly related or flagged with a precise blocker.

## Authority
Pilot dispatch after implementer evidence. User requested implement everything now.

## Allowed Scope
Review only. You may run commands and inspect diffs. Do not edit files unless a tiny review-note artifact is needed; prefer returning findings.

## Specific Exclusions
Do not implement Gate 2. Do not update docs for Gate 3. Do not commit, push, PR, or close the issue.

## Relevant Project Rules For This Gate
- Reviewer must check handoff compliance, quality, blockers, and evidence.
- Required region verification skipped is a blocker unless justified.
- New/changed interfaces must be clear at call boundary.
- Compatibility shims or dual execution paths are blockers without explicit need.
- Silent fallback or invalid input continuation is a defect.

## Required Context
- `.agent-work/issue-186-monte-carlo-contract/GATED_PLAN.md`
- `.agent-work/issue-186-monte-carlo-contract/crew-handoffs/gate-1-implementer.md`
- `.agent-work/issue-186-monte-carlo-contract/evidence/gate-1-implementation.md`
- `docs/agents/CREW_CONTEXT.md`
- Current git diff for Gate 1 files.

## Project Mechanics For This Gate
Review only. Do not commit, push, PR, or close the issue. You are not alone in the codebase; do not revert edits made by others.

## Required Evidence
Review verdict with blockers or approval, handoff compliance notes, tests/commands run, and residual risk.

## Required Verification Commands

```bash
py -m pytest tests/unit/strategy/test_classification_futures.py tests/unit/strategy/test_sample_futures.py tests/unit/strategy/test_sampled_runtime_bridge.py tests/unit/strategy/test_strategy_report_from_sampled_runtime.py tests/unit/strategy/test_fantasy_future_scoring.py tests/unit/strategy/test_fantasy_beam_search.py -v
```

Also run:

```bash
rg -n "max_futures|max-futures|sample_truncation" src/strategy scripts/generate_strategy_report_from_sampled_runtime.py
rg -n "src\\.evo_predictor|evo_predictor" src/strategy
```

## No-Test-Surface Rationale
Not applicable.

## Stop Conditions
Stop and return if required evidence cannot be produced, implementation touched out-of-scope areas with behavioral impact, or a blocker requires Pilot/user decision.

## Return Format
`APPROVE | BLOCK | COMMENT`, findings ordered by severity with file/line references, evidence commands, scope concerns, residual risk.
