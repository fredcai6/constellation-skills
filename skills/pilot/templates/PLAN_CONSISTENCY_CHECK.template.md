# Plan Consistency Check: `<work-id>`

Work file: `.agent-work/<work-id>/PLAN_CONSISTENCY_CHECK.md`

Purpose: verify that the problem framing, gated plan, structural baseline, authority, evidence, and Crew dispatch conditions agree before Pilot creates Crew handoffs.

Status values follow the Constellation workflow status model.

## Inputs

| Input | Path / Source | Status | Notes |
|---|---|---|---|
| User request | `<summary or source>` | `present | missing` | `<notes>` |
| Problem interrogation result | `.agent-work/<work-id>/PROBLEM_INTERROGATION_RESULT.md` | `present | missing | skipped because <reason>` | `<notes>` |
| Pilot checklist | `.agent-work/<work-id>/PILOT_CHECKLIST.md` | `present | missing` | `<notes>` |
| Gated plan | `.agent-work/<work-id>/GATED_PLAN.md` | `present | missing` | `<notes>` |
| Structural baseline | `<path/result or skipped because <reason>>` | `present | missing | skipped` | `<notes>` |
| Orchestrator context | `docs/agents/ORCHESTRATOR_CONTEXT.md` | `present | missing | not applicable` | `<notes>` |
| Crew context | `docs/agents/CREW_CONTEXT.md` | `present | missing | not applicable` | `<notes>` |

## Consistency Checks

### Intent and Scope

- [ ] Intent Protected is present and consistent across problem result, Pilot checklist, and gated plan.
- [ ] Scope, Not Scope, and Specific Exclusions agree across artifacts.
- [ ] No deferred/future work is pulled into current gates.
- [ ] Any rejected alternatives needed to prevent likely mistakes are recorded.

### Authority and Assumptions

- [ ] Every authority-sensitive action traces to user decision, project rule, task delegation, accepted default, or explicit assumption.
- [ ] Assumptions are either low-risk/reversible or blocking.
- [ ] Repo mechanics are explicit where needed: commit, PR, issue, archive, push, merge.

### Gate Quality

- [ ] Each gate is independently stoppable.
- [ ] Each gate has close criteria.
- [ ] Each gate has required evidence.
- [ ] Each gate has stop conditions.
- [ ] Each behavior-changing gate has a test/evidence mode.
- [ ] Each implementation gate has reviewer handoff planned or explicit skip reason.
- [ ] No Crew handoff would require hidden intent inference.

### Architecture / Structural Baseline

- [ ] Structural baseline need is resolved: `yes | no | skipped because <reason>`.
- [ ] Architecture-touching gates have reconciliation path.
- [ ] Structural uncertainty that affects ownership, dependency, scope, or evidence is routed to Cartographer or blocks dispatch.

### Verification / Evidence

- [ ] Required verification commands are exact, or explicitly absent with reason.
- [ ] Required evidence is inspectable by Pilot.
- [ ] Reviewer approval is not treated as sufficient by itself.
- [ ] Evidence integration path is clear per gate.

## Findings

| ID | Finding | Severity | Required action | Status |
|---|---|---|---|---|
| PC-001 | `<finding>` | `blocker | concern | note` | `<edit/ask/request/split>` | `open | resolved | accepted` |

## Verdict

`ready for Crew | revise plan | ask user | request Cartographer | split work | stop Pilot`

## Required Edits Before Dispatch

- `<edit or none>`

## Pilot Decision

`dispatch Crew | revise gated plan | ask user | request Cartographer baseline | split work | stop Pilot`

**Reason:** `<why>`
