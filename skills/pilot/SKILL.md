---
name: constellation-pilot
description: Use when managing Constellation workflow gates, scope, evidence, architecture checks, and closeout.
---

# Constellation Pilot

Pilot is a checklist-driven workflow controller for repo work expected to dispatch at least one bounded Crew implementer/reviewer handoff: intent, scope, gated plan, consistency, Crew dispatch, evidence, reconciliation, Triage candidates, closeout.

If no Crew handoff is needed, Pilot is not needed. Do not create Pilot artifacts, gated plans, or fake Crew handoffs. No fake lightweight Constellation path: no `.agent-work/`, no gated plan, no Crew handoff. Exit Pilot.

Pilot does not implement. Closeout integration edits need accepted evidence. Cartographer verifies architecture when structural truth may have changed.

## Checklist

Use `PILOT_CHECKLIST.md` as controller. Build `GATED_PLAN.md`, complete or override `PLAN_CONSISTENCY_CHECK.md`, then dispatch Crew.

Outcomes: `continue | ask user | split work | stop using Constellation | request Cartographer baseline | create gated plan | dispatch Crew | collect Triage candidate | close out`.

## Rules

Step 1 must invoke the `constellation-interrogator` skill for relentless one-question interrogation with `templates/PILOT_STARTING_QUESTIONS.template.md` as aggressively updated starting queue. Inspect repo/docs when they answer. Keep `.agent-work/<work-id>/INTERROGATOR_QUESTIONS.md`.

The gate is the central unit: smallest chunk assigned, reviewed, proven with evidence, and stopped independently. Implementation gates run: implementer Crew -> integrate evidence -> reviewer Crew -> integrate evidence -> gate close. Do not batch review at final closeout.

Pick agent strength from gate complexity, scope size, ambiguity, risk, review complexity. Dispatch Crew = create `CREW_HANDOFF`, kick off the assigned Crew subagent. Default sequential; parallel needs authorization and independent gates.

Pilot starts through Workbench templates: `PILOT_CHECKLIST`, `GATED_PLAN`, `PLAN_CONSISTENCY_CHECK`, `CREW_HANDOFF`, `EVIDENCE_INTEGRATION`. Workbench owns artifact hygiene; Pilot owns intent, scope, gates, evidence, Crew handoffs, reconciliation, Triage candidates, semantic closeout, closeout-only context curation. Done means Pilot moves the entire `.agent-work/<work-id>/` package to archive, including `INTERROGATOR_QUESTIONS.md`.

Issue/repo mechanics follow project Orchestrator context; ask if silent. Do not eagerly create issues. Create/link an issue only when the current gate cannot proceed without it and authority exists.

Templates: `templates/PILOT_CHECKLIST.template.md`, `templates/GATED_PLAN.template.md`, `templates/PLAN_CONSISTENCY_CHECK.template.md`, `templates/CREW_HANDOFF.template.md`, `templates/EVIDENCE_INTEGRATION.template.md`, `templates/PROBLEM_INTERROGATION_RESULT.template.md`.
