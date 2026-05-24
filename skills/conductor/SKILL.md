---
name: constellation-conductor
description: Use when work merits Constellation coordination: interrogate intent, bound scope, build gated plans, dispatch Crew, integrate evidence, reconcile architecture, collect Triage candidates, and close out.
---

# Constellation Conductor

Conductor is a checklist-driven workflow controller: intent, scope, Constellation value, baseline, gated plan, Crew dispatch, evidence, architecture reconciliation, Triage candidates, closeout.

If no Crew handoff is needed, Constellation is not needed. No fake lightweight Constellation path: no `.agent-work/`, no gated plan, no Crew handoff. Exit Conductor.

Conductor does not implement gated code/product work. Closeout integration edits need accepted evidence. Cartographer verifies architecture when structural truth may have changed.

## Checklist

0. Load project context. 1. Interrogate request. 2. Bound problem. 3. Decide whether Constellation adds value. 4. Establish structural baseline. 5. Build gated plan. 6. Dispatch Crew. 7. Integrate evidence. 8. Check architecture reconciliation. 9. Collect Triage candidates. 10. Semantic closeout.

Outcomes: `continue | ask user | split work | stop using Constellation | request Cartographer baseline | create gated plan | dispatch Crew | collect Triage candidate | close out`.

## Rules

Step 1 must invoke the `grill-me` skill for relentless one-question interrogation. Inspect repo/docs only when they answer. Pre-decision inspection is artifact-free unless recovery state needed.

The gate is the central unit: smallest chunk assigned, reviewed, proven with evidence, and stopped independently. Implementation gates run: implementer Crew -> integrate evidence -> reviewer Crew -> integrate evidence -> gate close. Do not batch review at final closeout.

Pick agent strength from gate complexity, scope size, ambiguity, risk, review complexity. Dispatch Crew = create `CREW_HANDOFF`, kick off the assigned Crew subagent for that gate. Default sequential; parallel needs explicit authorization and independent gates.

Conductor starts workflow through Workbench templates: `CONDUCTOR_CHECKLIST`, `GATED_PLAN`, `CREW_HANDOFF`, `EVIDENCE_INTEGRATION`. Workbench owns artifact hygiene; Conductor owns intent, scope, gates, evidence, Crew handoffs, reconciliation, Triage candidates, semantic closeout, closeout-only context curation.

Issue/repo mechanics follow project Orchestrator context; ask if silent. Do not eagerly create issues. Create/link an issue only when the current gate cannot proceed without it and authority exists.

Templates: `templates/CONDUCTOR_CHECKLIST.template.md`, `templates/GATED_PLAN.template.md`, `templates/CREW_HANDOFF.template.md`, `templates/EVIDENCE_INTEGRATION.template.md`, `templates/PROBLEM_INTERROGATION_RESULT.template.md`.
