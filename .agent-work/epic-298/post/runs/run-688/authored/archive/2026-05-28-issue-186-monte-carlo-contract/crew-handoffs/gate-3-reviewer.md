# Crew Handoff

## Role
`reviewer`

## Assigned Gate
`Gate 3: Durable Docs, Report Schemas, And Region Verification`

## Suggested Model Tier
`simple bounded, because this is docs/schema cleanup plus verification evidence`

## Test Mode
`review required; rerun targeted inspection commands if useful`

## Task
Review Gate 3 documentation and evidence. Verify docs match the approved Gate 1 and Gate 2 contracts, do not contain stale v1/truncation/DNF contract language, have correct `Last verified` dates where required, and architecture reconciliation recommendation is sound.

## Intent Protected
Docs must match code/tests and preserve the strategy/evo contract boundary.

## Close Criteria
- Docs describe `ClassificationFutureSet` v2, `FinalOrderSampleSet` v2, stage snapshots, no truncation, fixture vs production artifact distinction, and strategy/evo boundary.
- Stale `DNF_POSITION = 30` contract language and `max_futures` schema language are removed or reframed.
- Full affected region suites were run and passed.
- Architecture reconciliation decision is recorded.

## Authority
Pilot dispatch after Gate 3 implementer evidence. Gates 1 and 2 are approved.

## Allowed Scope
Review only. You may inspect docs/diff and run commands. Do not edit files unless a tiny review-note artifact is needed; prefer returning findings.

## Specific Exclusions
Do not edit code/docs, commit, push, PR, merge, or close the issue.

## Relevant Project Rules For This Gate
- Docs must not contradict code/tests.
- Command examples must match current CLI flags.
- Command-heavy docs require current `Last verified` date when touched.
- GLOSSARY.md must be terminology only, not an implementation spec.

## Required Context
- `.agent-work/issue-186-monte-carlo-contract/GATED_PLAN.md`
- `.agent-work/issue-186-monte-carlo-contract/evidence/gate-1-review-approve.md`
- `.agent-work/issue-186-monte-carlo-contract/evidence/gate-2-review-approve.md`
- `.agent-work/issue-186-monte-carlo-contract/evidence/gate-3-implementation.md`
- `docs/agents/CREW_CONTEXT.md`
- Current git diff for docs touched by Gate 3.

## Project Mechanics For This Gate
Review only. Do not commit, push, PR, merge, or close the issue.

## Required Evidence
Review verdict with blockers or approval, file/line references for findings, commands/inspections run, architecture reconciliation recommendation, residual risk.

## Required Verification Commands

```bash
rg -n "ClassificationFutureSet v1|max_futures|max-futures|sample_truncation|DNF_POSITION = 30|schema_version\": 1" docs/evo/sampled_runtime_strategy_contract.md docs/report_schemas/strategy_reports.md docs/report_schemas/README.md docs/agents/GLOSSARY.md
```

Full unit commands were already run by implementer; rerun only if reviewer thinks evidence is insufficient.

## No-Test-Surface Rationale
Docs review uses inspection; test evidence is from Gate 3 implementation.

## Stop Conditions
Stop and return if docs contradict code/tests, stale language remains, glossary becomes implementation spec, or architecture reconciliation needs Cartographer.

## Return Format
`APPROVE | BLOCK | COMMENT`, findings ordered by severity with file/line references, evidence commands/inspection, architecture reconciliation recommendation, residual risk.
