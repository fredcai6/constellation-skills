# Pilot Checklist: `<work-id>`

Work file: `.agent-work/<work-id>/PILOT_CHECKLIST.md`. Pilot's single execution controller. Status values follow `skills/workbench/references/status-model.md`. Skipped gates require `skipped because <reason>`. Each gate close needs evidence.

## Task

`<one-paragraph task summary>`

## Source

**Work ID:** `<work-id>`  
**Handoff/framing source:** `<path/title or summary>`  
**Authority:** `<user decision | project rule | delegated | default | assumption>`

## Workflow State

**User request:** `<what user asked for>`  
**Interpreted intent:** `<what work is meant to accomplish>`  
**Intent protected:** `<outcome that must not be lost>`  
**Scope:** `<current work boundary>`  
**Not scope:** `<deferred/outside work>`  
**Specific exclusions:** `<in-scope-looking areas protected>`  
**Success evidence:** `<observable proof if succeeds>`  
**Rejected alternatives:** `<only when needed to clarify boundaries; else none>`

## Ambiguity / Authority

**Resolved ambiguities:** `<decisions + source>`  
**Remaining ambiguity:** `<none | question + blocking status>`

| Assumption | Authority | Risk |
|---|---|---|
| `<assumption>` | `<user/project rule/repo artifact/Pilot default>` | `<low reversible | blocking>` |

## Definition of Done

- [ ] `<completion criterion>`
- [ ] `<evidence criterion>`
- [ ] `<reporting criterion>`

## Gates

| Gate | Status | Criteria | Evidence / note |
|---|---|---|---|
| 0. Load project context | pending | Orchestrator/Crew context, Workbench, relevant docs loaded | `<note>` |
| 1. Interrogate request | pending | `constellation-interrogator` invoked; `INTERROGATOR_QUESTIONS.md` saved; Workflow State + Ambiguity populated | `<note>` |
| 2. Bound problem | pending | scope/not-scope/specific exclusions agreed | `<note>` |
| 3. Decide Constellation value | pending | Crew handoff need + added-value reason recorded; else stop using Constellation | `<continue \| stop>` |
| 4. Establish structural baseline | pending | baseline established, Cartographer requested, or skipped because `<reason>` | `<note>` |
| 5. Define implementation gates | pending | Implementation Gates section populated; Plan Consistency Criteria below met or each gap has recorded override reason | `<verdict + evidence>` |
| 6. Execute implementation gates | pending | every implementation gate closed (continue, cancelled, or redirected with reason); no batched review | `<note>` |
| 7. Architecture reconciliation | pending | `no action \| Pilot packet edit \| request Cartographer verification \| Triage candidate` | `<verdict>` |
| 8. Collect Triage candidates | pending | `none \| logged \| routed \| dropped because <reason>` | `<note>` |
| 9. Semantic closeout | pending | Semantic Closeout criteria below satisfied | `<note>` |

## Plan Consistency Criteria

Gate 5 closes only when each holds or has recorded override reason:

- Intent Protected consistent across artifacts
- Scope / Not Scope / Specific Exclusions agree across artifacts
- No deferred/future work pulled into current gates
- Every authority-sensitive action traces to user decision, project rule, delegation, accepted default, or recorded assumption
- Assumptions either low-risk/reversible or blocking
- Repo mechanics explicit (commit, PR, issue, archive, push, merge)
- Each implementation gate independently stoppable
- Each implementation gate has goal, close criteria, required evidence, stop conditions
- Each behavior-changing gate has test/evidence mode
- Each implementation gate has reviewer handoff planned or explicit skip reason
- No Crew handoff would require hidden intent inference
- Structural baseline need resolved (yes / no / skipped because `<reason>`)
- Architecture-touching gates have reconciliation path
- Structural uncertainty affecting ownership / dependency / scope / evidence routed to Cartographer or blocks dispatch
- Required verification commands exact or explicitly absent with reason
- Required evidence inspectable by Pilot
- Reviewer approval not treated as sufficient alone
- Evidence integration path clear per gate

## Implementation Gates

Pilot defines in gate 5, executes in gate 6. Each gate runs: implementer Crew -> integrate evidence -> reviewer Crew -> integrate evidence -> gate close. Do not batch review at final closeout.

### Implementation Gate I1: `<name>`

**Purpose:** `<why this gate exists>`  
**Suggested model tier:** `<simple bounded | stronger broad/ambiguous, because <reason>>`  
**Test mode:** `<TDD required | test-after allowed | inspection-only because <reason>>`  
**Allowed scope:** `<files/regions>`  
**Specific exclusions:** `<narrowed exclusions | none>`  
**Stop conditions:** `<when this gate returns to Pilot/user>`

**Close criteria:**
- [ ] `<observable condition>`
- [ ] implementer evidence integrated
- [ ] reviewer evidence integrated, or skipped because `<reason>`

**Required evidence:** `<test command | content assertion | diff inspection | render/build output | review result | Cartographer verification | user decision>`

**Required verification commands:**
```bash
<exact command or none because <reason>>
```

**Implementer dispatch:**
- Handoff: `<crew-handoffs/<gate>-implementer.md or not applicable because <reason>>`
- Subagent kickoff: `<id/result>`
- Return status: `<complete | partial | blocked | out-of-scope | failed>`
- Implementation evidence: `<tests, commands, diff inspection, generated output>`
- Original intent check: `<satisfies | concern>`
- Scope drift check: `<in allowed scope | concern | exceeded | specific exclusion touched>`
- Assumption check: `<still holds | changed | now blocking | none>`
- New information: `<ambiguity | decision | structural change | Triage candidate | none>`
- Pilot decision: `<continue | send back | revise plan | request Cartographer | collect Triage | stop>`

**Reviewer dispatch:**
- Handoff: `<crew-handoffs/<gate>-reviewer.md or skipped because <reason>>`
- Subagent kickoff: `<id/result>`
- Return verdict: `<APPROVE | BLOCK | COMMENT>`
- Review evidence: `<handoff compliance, quality, blocker status, reconciliation check>`
- Reviewer approval alone insufficient: acknowledged
- Pilot decision: `<continue | send back | revise plan | request Cartographer | collect Triage | stop>`

**Gate close:** `pending | complete | cancelled because <reason> | redirected because <reason>`

## Execution Notes

### Gate `<n>`: `<short title>`

**Status transitions:** `<pending -> in-progress -> complete/blocked/skipped>`  
**What happened:** `<brief recovery-useful note>`  
**Evidence:** `<test, file, inspection, command, review result>`  
**Follow-up:** `<none or next action>`

## Current State

**Last completed gate:** `<gate>`  
**Current blocker:** `<none or blocker>`  
**Next recommended action:** `<what next agent should do first>`  
**Files/artifacts touched:** `<list>`  
**Open assumptions:** `<list or none>`

## Project Mechanics

Project mechanics follow project Orchestrator context; ask if silent. Record repo action authority, commit sensitivity, whether Pilot may open PRs directly, and whether Pilot may merge to main.

| Hook | Status | Evidence / link |
|---|---|---|
| `<gate/action>` | `<pending | complete | blocked | skipped>` | `<commit SHA / issue comment link or id / PR URL / branch / approval note>` |

## Triage Candidates

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
- [ ] implementation gates each completed Crew cycle; review not batched
- [ ] required evidence recorded
- [ ] reviewer evidence integrated; reviewer approval alone insufficient
- [ ] assumptions still hold or were resolved
- [ ] architecture reconciliation checked
- [ ] Triage candidates routed, dropped because `<reason>`, or none
- [ ] route/apply/drop template update candidates from closeout
- [ ] project-required repo actions approved and evidenced
- [ ] Pilot moved entire `.agent-work/<work-id>/` package to `.agent-work/archive/<date>-<work-id>/`, including `INTERROGATOR_QUESTIONS.md`; no loose work-id artifacts remain
- [ ] Workbench artifact closeout `complete | pending because <reason> | skipped because <reason>`
