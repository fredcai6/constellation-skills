# Pilot Checklist: `<work-id>`

Work file: `.agent-work/<work-id>/PILOT_CHECKLIST.md`

This is the active workflow controller for Pilot. LOCAL_TODO is recovery metadata, not the execution checklist.

Status values: `pending | in-progress | blocked | complete | skipped`

Skipped steps require `skipped because <reason>`.

## Workflow State

**LOCAL_TODO:** `<current | pending | blocked, see Workbench>`  
**Intent protected:** `<user/system outcome that must not be lost>`  
**Scope:** `<current work boundary>`  
**Not scope:** `<deferred or outside work>`  
**Specific exclusions:** `<in-scope-looking areas protected from this work>`

## Ambiguity / Authority

**Resolved ambiguities:** `<decisions, sources>`  
**Remaining ambiguities:** `<none | question + blocking status>`  
**Assumptions:** `<low-risk reversible assumptions + authority, or none>`

## Checklist

| Step | Status | Evidence / note |
|---|---|---|
| 0. Load project context | pending | `<Orchestrator/Crew context, Workbench, relevant docs>` |
| 1. Interrogate request | pending | `<constellation-interrogator invoked; INTERROGATOR_QUESTIONS.md path; resolved intent + success evidence, or skipped because repo/docs answered>` |
| 2. Bound problem | pending | `<scope/not-scope/specific exclusions>` |
| 3. Decide whether Constellation adds value | pending | `<Crew handoff need + value reason>` |
| 4. Establish structural baseline | pending | `<continue | request Cartographer baseline | skipped because ...>` |
| 5. Build gated plan | pending | `<GATED_PLAN.md path>` |
| 6. Dispatch Crew | pending | `<CREW_HANDOFF path + subagent kickoff id/result, or cancelled/redirected because ...>` |
| 7. Integrate evidence | pending | `<per-gate evidence integration: implementer evidence, reviewer evidence, gate close decision>` |
| 8. Check architecture reconciliation | pending | `<no action | Pilot packet edit | request Cartographer verification | Triage candidate>` |
| 9. Collect Triage candidates | pending | `<none | logged | routed | dropped because ...>` |
| 10. Semantic closeout | pending | `<complete | blocked | skipped because ...>` |

## Project Mechanics Status

Project mechanics follow project Orchestrator context; ask if silent.

| Hook | Status | Evidence / link |
|---|---|---|
| `<gate/action>` | `<pending | complete | blocked | skipped>` | `<commit SHA / issue comment link or id / PR URL / branch / approval note>` |

## Triage Candidates For Closeout

### Triage candidate: `<short title>`

**Reason:** `<missing implementation | desired redesign | stale future doc | unresolved decision | discovered follow-up>`  
**Current work anchor:** `<gate / file / issue / review finding>`  
**Structural anchor:** `struct:<id> | path | none`  
**Current truth:** `<what exists now>`  
**Future concern:** `<outside current scope>`  
**Evidence:** `<paths / commands / review finding>`  
**Recommended Triage action:** `<issue-ready recommendation scope>`

## Semantic Closeout

- [ ] all gates complete, cancelled, or redirected with reason
- [ ] required evidence recorded
- [ ] reviewer evidence integrated; reviewer approval alone is insufficient
- [ ] assumptions still hold or were resolved
- [ ] architecture reconciliation checked
- [ ] Triage candidates routed, dropped because `<reason>`, or none
- [ ] project-required repo actions approved and evidenced
- [ ] Workbench artifact closeout `complete | pending because <reason> | skipped because <reason>`
