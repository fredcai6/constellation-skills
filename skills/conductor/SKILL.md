---
name: constellation-conductor
description: Use when work merits Constellation coordination: interrogate intent, bound scope, build gated plans, dispatch Crew, integrate evidence, reconcile architecture, collect Triage candidates, and close out.
---

# Constellation Conductor

## Mission

Conductor is a checklist-driven workflow controller for work that merits Constellation. It interrogates intent, bounds scope, decides whether Constellation adds value, establishes baseline, creates a gated plan, dispatches Crew, integrates evidence, checks architecture reconciliation, collects Triage candidates, and closes out.

If no Crew handoff is needed, Constellation is not needed. No fake lightweight Constellation path: no `.agent-work/`, no gated plan, no Crew handoff. Exit Conductor and continue only under normal direct-work rules.

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

Interrogate intent relentlessly, one question at a time; inspect repo/docs instead when they answer. Pre-decision inspection is artifact-free unless recovery state is needed, which starts Constellation and requires coherent closeout.

The gate is the central unit: smallest chunk that can be assigned, reviewed, proven with evidence, and stopped independently. Pick agent strength from gate complexity, scope size, ambiguity, risk, and review complexity. Default Crew dispatch is sequential; parallel dispatch needs explicit authorization and independent gates.

Conductor starts workflow execution through Workbench: use `CONDUCTOR_CHECKLIST`, `GATED_PLAN`, `CREW_HANDOFF`, and `EVIDENCE_INTEGRATION` as the execution surface. Workbench owns artifact hygiene; Conductor owns intent, scope, gates, evidence requirements, Crew handoffs, architecture reconciliation decisions, Triage candidates, semantic closeout, and closeout-only context curation.

Issue/repo mechanics follow project Orchestrator context; ask if silent. Do not eagerly create issues. Create/link an issue only when the current gate cannot proceed without it and authority exists.
