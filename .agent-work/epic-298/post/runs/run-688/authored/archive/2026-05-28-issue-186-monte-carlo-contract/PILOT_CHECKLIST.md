# Pilot Checklist: `issue-186-monte-carlo-contract`

Work file: `.agent-work/issue-186-monte-carlo-contract/PILOT_CHECKLIST.md`

This is the active workflow controller for Pilot. LOCAL_TODO is recovery metadata, not the execution checklist.

## Workflow State

**LOCAL_TODO:** `current`  
**Intent protected:** `Resolve issue #186 by creating a clear, tested, documented contract for Monte Carlo sampled-race results crossing from sampled evo runtime to strategy/fantasy layers, without hidden compatibility paths or fuzzy boundary semantics.`  
**Scope:** `Issue interrogation, gated plan, strategy/evo contract code or docs selected by the resolved plan, tests, and evidence integration.`  
**Not scope:** `Gold training reruns, real-data prediction quality changes, pushing/opening PR/closing issue without explicit user approval.`  
**Specific exclusions:** `Do not manually edit generated gold outputs or bulky runtime artifacts. Do not add FastF1 access from strategy/evo analysis paths.`

## Ambiguity / Authority

**Resolved ambiguities:** `Issue comments decide: strategy consumes ClassificationFutureSet only; no evo internals across strategy boundary; futures move to index array v2; no truncation feature; DNF/DNS status stays out of current sampled contract; FinalOrderSampleSet gains versioning and typed stage snapshots. User confirmed implementation depth: implement everything now.`  
**Remaining ambiguities:** `none`  
**Assumptions:** `none`

## Checklist

| Step | Status | Evidence / note |
|---|---|---|
| 0. Load project context | complete | `Read docs/AGENT_GUIDE.md, README.md, TESTING.md, docs/architecture/index.md, docs/DOCUMENTATION.md, docs/agents/ORCHESTRATOR_CONTEXT.md, docs/agents/CREW_CONTEXT.md, docs/agents/GLOSSARY.md.` |
| 1. Interrogate request | complete | `constellation-interrogator invoked; .agent-work/issue-186-monte-carlo-contract/INTERROGATOR_QUESTIONS.md and PROBLEM_INTERROGATION_RESULT.md. Q1 answered by user: implement everything now.` |
| 2. Bound problem | complete | `Scope/not-scope/specific exclusions recorded in PROBLEM_INTERROGATION_RESULT.md.` |
| 3. Decide whether Constellation adds value | complete | `Use Constellation because this is a multi-region contract boundary with implementation and reviewer gates.` |
| 4. Establish structural baseline | complete | `No new Cartographer baseline needed; docs/architecture/index.md verified 2026-05-26 and boundary is known: evo owns runtime, strategy owns adapter/fantasy.` |
| 5. Build gated plan | complete | `.agent-work/issue-186-monte-carlo-contract/GATED_PLAN.md` |
| 5a. Plan consistency check | complete | `.agent-work/issue-186-monte-carlo-contract/PLAN_CONSISTENCY_CHECK.md verdict: ready for Crew` |
| 6. Dispatch Crew | complete | `Gate 1, Gate 2, and Gate 3 implementer/reviewer cycles complete.` |
| 7. Integrate evidence | complete | `All gate evidence and reviewer approvals recorded under .agent-work/issue-186-monte-carlo-contract/evidence/.` |
| 8. Check architecture reconciliation | complete | `No architecture map update required; contracts changed inside existing evo/strategy boundaries.` |
| 9. Collect Triage candidates | complete | `None.` |
| 10. Semantic closeout | complete | `.agent-work/issue-186-monte-carlo-contract/WORKFLOW_CLOSEOUT.md` |

## Project Mechanics Status

Project mechanics follow project Orchestrator context. Local branch/workflow artifacts/code/docs/test runs are authorized. Ask before push, PR, merge, delete, close issue.

| Hook | Status | Evidence / link |
|---|---|---|
| branch | complete | `codex/issue-186-mc-contract` |
| push/PR/merge/close | blocked | `Requires explicit user approval.` |

## Triage Candidates For Closeout

None yet.

## Semantic Closeout

- [x] all gates complete, cancelled, or redirected with reason
- [x] plan consistency check completed, or skipped because `<reason>` with dispatch override recorded
- [x] required evidence recorded
- [x] reviewer evidence integrated; reviewer approval alone is insufficient
- [x] assumptions still hold or were resolved
- [x] architecture reconciliation checked
- [x] Triage candidates routed, dropped because `none`, or none
- [x] route/apply/drop template update candidates from closeout
- [x] project-required repo actions approved and evidenced
- [x] Pilot moved the entire `.agent-work/issue-186-monte-carlo-contract/` package to `.agent-work/archive/2026-05-28-issue-186-monte-carlo-contract/`, including `INTERROGATOR_QUESTIONS.md`; no loose work-id artifacts remain
- [x] Workbench artifact closeout `complete`
