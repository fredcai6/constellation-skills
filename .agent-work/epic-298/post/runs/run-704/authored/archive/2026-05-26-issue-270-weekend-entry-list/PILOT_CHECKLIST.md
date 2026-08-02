# Pilot Checklist: issue-270-weekend-entry-list

Work file: `.agent-work/issue-270-weekend-entry-list/PILOT_CHECKLIST.md`

## Workflow State

**LOCAL_TODO:** current  
**Intent protected:** Training feature construction must use a pre-weekend driver field when available, without adding non-DB analysis reads or breaking historical DBs without entry-list rows.  
**Scope:** Issue #270 data schema/query/collector support and `build_all_race_features` eligible-driver selection.  
**Not scope:** Historical backfill, prediction-time path changes, FastF1 calls from evo/analysis code, unrelated leakage redesign.  
**Specific exclusions:** Existing untracked report artifacts; issue #253 workflow package; sampled-runtime prediction explicit eligible-driver path.

## Ambiguity / Authority

**Resolved ambiguities:** Interrogator file records that the issue requires DB storage, fallback for missing lists, and no historical backfill.  
**Remaining ambiguities:** none.  
**Assumptions:** FastF1 `session.drivers` is acceptable at ingestion time as the requested pre-weekend source; if unavailable/empty, collector skips storing rows and training falls back.

## Checklist

| Step | Status | Evidence / note |
|---|---|---|
| 0. Load project context | complete | `docs/AGENT_GUIDE.md`, `README.md`, `TESTING.md`, `docs/architecture/index.md`, `docs/DOCUMENTATION.md`, `docs/agents/ORCHESTRATOR_CONTEXT.md`, `docs/agents/CREW_CONTEXT.md` |
| 1. Interrogate request | complete | `.agent-work/issue-270-weekend-entry-list/INTERROGATOR_QUESTIONS.md`; repo/docs answered blocking questions |
| 2. Bound problem | complete | scope/not-scope/exclusions above |
| 3. Decide whether Constellation adds value | complete | schema + data + evo training impact needs implementation and reviewer Crew evidence |
| 4. Establish structural baseline | complete | Architecture index: data layer owns schema/ingestion; evo depends on DB and must not call FastF1 |
| 5. Build gated plan | complete | `.agent-work/issue-270-weekend-entry-list/GATED_PLAN.md` |
| 5a. Plan consistency check | complete | `.agent-work/issue-270-weekend-entry-list/PLAN_CONSISTENCY_CHECK.md`: ready for Crew |
| 6. Dispatch Crew | complete | implementer Crew `Feynman`; reviewer Crews `Banach` then `Hubble` after blocker fixes |
| 7. Integrate evidence | complete | `.agent-work/issue-270-weekend-entry-list/evidence/GATE1_EVIDENCE_INTEGRATION.md`; final verification green |
| 8. Check architecture reconciliation | complete | no map update needed; ownership remains data schema/ingestion plus evo DB consumer |
| 9. Collect Triage candidates | complete | none |
| 10. Semantic closeout | complete | user authorized archive, push/merge to main, and issue close |

## Project Mechanics Status

| Hook | Status | Evidence / link |
|---|---|---|
| branch | complete | initial branch `codex/issue-270-weekend-entry-list`; final fixes on `codex/issue-270-entry-list-review-fixes` |
| commit/push/PR | blocked | push/PR require user approval per Orchestrator context |

## Triage Candidates For Closeout

None currently.

## Semantic Closeout

- [x] all gates complete, cancelled, or redirected with reason
- [x] plan consistency check completed
- [x] required evidence recorded
- [x] reviewer evidence integrated; reviewer approval alone is insufficient
- [x] assumptions still hold or were resolved
- [x] architecture reconciliation checked
- [x] Triage candidates routed, dropped because reason, or none
- [x] route/apply/drop template update candidates from closeout
- [x] project-required repo actions approved and evidenced
- [x] Pilot moved the entire `.agent-work/issue-270-weekend-entry-list/` package to `.agent-work/archive/2026-05-26-issue-270-weekend-entry-list/`, including `INTERROGATOR_QUESTIONS.md`; no loose work-id artifacts remain
- [x] Workbench artifact closeout complete
