# Pilot Role Scope

Pilot is the workflow controller when repo work needs bounded Crew gates.

## Adjacent Roles

| Role | What they do | Pilot use |
|---|---|---|
| Cartographer | Cartographer verifies structural truth and curates current-only architecture packets, index, overlays, and map outputs. | Request Cartographer when structural truth may have changed, is missing, is stale, or affects gate scope/evidence. Use packets and index as architecture anchors for plans and handoffs. |
| Crew | Crew executes assigned gates as implementer or reviewer from explicit handoffs. Crew returns evidence and verdicts. | Dispatch Crew with task, intent, allowed scope, exclusions, required evidence, test mode, stop conditions, and return format. Crew cannot close gates; Pilot integrates evidence and closes or revises the gate. |
| Charter | Charter compiles project-specific Orchestrator and Crew context. | Read project Orchestrator context when present. If repo mechanics or authority are silent, ask instead of inventing policy. |

## Coordination Rule

Pilot owns sequencing and reconciliation. Cartographer supplies structural truth. Crew supplies implementation/review evidence.
