# Crew Handoff

## Role
`implementer`

## Assigned Gate
`Gate 3: Durable Docs, Report Schemas, And Region Verification`

## Suggested Model Tier
`simple bounded, because this is docs/schema cleanup plus verification`

## Test Mode
`test-after allowed; docs inspection plus region suites`

## Task
Update durable docs/report schema truth for issue #186 after Gates 1 and 2. Remove stale v1/truncation language, document `ClassificationFutureSet` v2, `FinalOrderSampleSet` v2, `StageSnapshot`, production-vs-fixture distinction, and the truthful fail-fast behavior for filtered scoring when per-stage snapshots cannot be reconstructed. Run final verification commands.

## Intent Protected
Docs must match code/tests and preserve the strategy/evo contract boundary. Do not invent future work or contradict Gate 1/Gate 2 decisions.

## Close Criteria
- Docs describe `ClassificationFutureSet` v2, `FinalOrderSampleSet` v2, stage snapshots, no truncation, fixture vs production artifact distinction, and strategy/evo boundary.
- Stale `DNF_POSITION = 30` contract language and `max_futures` schema language are removed or reframed.
- Full affected region suites are run or failures documented.
- Architecture reconciliation decision recorded.

## Authority
User requested implementation now. Gate 1 and Gate 2 approved. Orchestrator requires docs to stay current with code/tests.

## Allowed Scope
`docs/evo/sampled_runtime_strategy_contract.md`, `docs/report_schemas/strategy_reports.md`, `docs/report_schemas/README.md`, any docs directly contradicted by Gates 1-2, final evidence files under `.agent-work/issue-186-monte-carlo-contract/evidence/`.

## Specific Exclusions
Do not create new future-looking docs outside the issue scope. Do not update architecture map unless implementation changed structural relationships. Do not edit code unless a doc verification command reveals a trivial typo in test command references and Pilot approves first. Do not commit, push, PR, merge, or close issue.

## Relevant Project Rules For This Gate
- Docs must not contradict current repo workflow or test practice.
- Command-heavy docs need current commands and `Last verified` date.
- Full region suite for affected regions before finalizing.
- Use `py`, not `python`.

## Required Context
- `.agent-work/issue-186-monte-carlo-contract/GATED_PLAN.md`
- `.agent-work/issue-186-monte-carlo-contract/evidence/gate-1-review-approve.md`
- `.agent-work/issue-186-monte-carlo-contract/evidence/gate-2-review-approve.md`
- `docs/agents/CREW_CONTEXT.md`
- `docs/evo/sampled_runtime_strategy_contract.md`
- `docs/report_schemas/strategy_reports.md`

## Project Mechanics For This Gate
Do not commit, push, PR, or close the issue. Edit directly in the current workspace. You are not alone in the codebase; do not revert edits made by others.

## Required Evidence
Diff summary, docs inspection notes, verification command output summary, blockers if any, and architecture reconciliation recommendation.

## Required Verification Commands

```bash
py -m pytest tests/unit/evo_predictor/ -v
py -m pytest tests/unit/ -v
```

If the full `tests/unit/ -v` command fails, report whether failures are caused by current changes or unrelated existing issues, with failing test names.

## No-Test-Surface Rationale
Docs are inspection-verified, but final region suites are required because Gates 1-2 changed code.

## Stop Conditions
Stop and return if region suite failure needs code changes outside Gate 3 docs scope, docs require a new architecture decision, or generated reports must be regenerated instead of docs updated.

## Return Format
Diff summary, files changed, tests run with pass/fail result, architecture reconciliation recommendation, blockers, scope concerns, assumptions used.
