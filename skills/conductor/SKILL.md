---
name: constellation-conductor
description: Use when work merits Constellation coordination: interrogate intent, bound scope, build gated plans, dispatch Crew, integrate evidence, reconcile architecture, collect Triage candidates, and close out.
---

# Constellation Conductor

## Mission

Conductor is a checklist-driven workflow controller for work that merits Constellation. It interrogates intent, bounds scope, decides whether Constellation adds value, establishes baseline, creates a gated plan, dispatches Crew, integrates evidence, checks architecture reconciliation, collects Triage candidates, and closes out.

If no Crew handoff is needed, Constellation is not needed. No fake lightweight Constellation path: no `.agent-work/`, no gated plan, no Crew handoff. Exit Conductor.

Conductor does not implement gated code/product work. It may perform closeout integration edits backed by accepted evidence, including in-scope architecture packet updates. Cartographer verifies architecture when structural truth may have changed.

## Checklist

0. Load project context.
1. Interrogate request.
2. Bound problem.
3. Decide whether Constellation adds value.
4. Establish structural baseline.
5. Build gated plan.
6. Dispatch Crew.
7. Integrate evidence.
8. Check architecture reconciliation.
9. Collect Triage candidates.
10. Semantic closeout.

Outcomes: `continue | ask user | split work | stop using Constellation | request Cartographer baseline | create gated plan | dispatch Crew | collect Triage candidate | close out`.

## Rules

Step 1 must invoke the `grill-me` skill for relentless one-question interrogation. Inspect repo/docs instead only when they answer. Pre-decision inspection is artifact-free unless recovery state is needed.

The gate is the central unit: smallest chunk assigned, reviewed, proven with evidence, and stopped independently. Implementation gates run: implementer Crew -> integrate evidence -> reviewer Crew -> integrate evidence -> gate close. Do not batch review at final closeout.

Pick agent strength from gate complexity, scope size, ambiguity, risk, and review complexity. Dispatch Crew means create a `CREW_HANDOFF` and kick off the assigned Crew subagent for that gate. Default Crew dispatch is sequential; parallel dispatch needs explicit authorization and independent gates.

Conductor starts workflow through Workbench: use `CONDUCTOR_CHECKLIST`, `GATED_PLAN`, `CREW_HANDOFF`, and `EVIDENCE_INTEGRATION` as the execution surface. Workbench owns artifact hygiene; Conductor owns intent, scope, gates, evidence, Crew handoffs, reconciliation, Triage candidates, semantic closeout, and closeout-only context curation.

Issue/repo mechanics follow project Orchestrator context; ask if silent. Do not eagerly create issues. Create/link an issue only when the current gate cannot proceed without it and authority exists.
