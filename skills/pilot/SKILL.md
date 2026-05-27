---
name: constellation-pilot
description: Use when managing Constellation workflow gates, scope, evidence, architecture checks, and closeout.
---

# Constellation Pilot

Pilot is a checklist-driven workflow controller for repo work expected to dispatch at least one bounded Crew implementer/reviewer handoff: intent, scope, implementation gates, consistency, Crew dispatch, evidence, reconciliation, Triage candidates, closeout.

Pilot does not implement. Closeout integration edits need accepted evidence. Cartographer verifies architecture when structural truth may have changed.

If no Crew handoff is needed, Pilot is not needed: no `.agent-work/`, no implementation gates, no fake lightweight Constellation path.

## Checklist

Use `PILOT_CHECKLIST.md` as single controller. Framing gates (0-4), Implementation gates (5-6) populated and executed in the Implementation Gates section, Closing gates (7-9).

Outcomes: `continue | ask user | split work | stop using Constellation | request Cartographer baseline | define implementation gates | dispatch Crew | collect Triage candidate | close out`.

## Rules

Gate 1 must invoke the `constellation-interrogator` skill for relentless one-question interrogation with `templates/PILOT_STARTING_QUESTIONS.template.md` as aggressively updated starting queue. Inspect repo/docs when they answer. Keep `.agent-work/<work-id>/INTERROGATOR_QUESTIONS.md`. Not optional; do not skip.

The gate is the central unit: smallest chunk assigned, reviewed, proven with evidence, and stopped independently. Implementation gates run: implementer Crew -> integrate evidence -> reviewer Crew -> integrate evidence -> gate close. Do not batch review at final closeout.

Pick agent strength from gate complexity, scope size, ambiguity, risk, review complexity. Dispatch Crew = create `CREW_HANDOFF`, kick off the assigned Crew subagent. Default sequential; parallel needs authorization and independent gates.

Gate 5 closes only when Plan Consistency Criteria met or each gap has recorded override reason. Pilot writes implementation gate sub-sections directly in `PILOT_CHECKLIST.md`. Evidence integration is recorded in each implementation gate's sub-section as Crew returns.

Workbench owns artifact hygiene; Pilot owns intent, scope, gates, evidence, Crew handoffs, reconciliation, Triage candidates, semantic closeout, closeout-only context curation. Done means Pilot moves the entire `.agent-work/<work-id>/` package to archive, including `INTERROGATOR_QUESTIONS.md`.

Issue/repo mechanics follow project Orchestrator context; ask if silent. Do not eagerly create issues. Create/link an issue only when the current gate cannot proceed without it and authority exists.

Templates: `templates/PILOT_CHECKLIST.template.md`, `templates/CREW_HANDOFF.template.md`. Reference: `references/role-scope.md`.
