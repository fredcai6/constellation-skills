# Cartographer Role Scope

Cartographer verifies and curates current-only structural truth. It does not implement, plan feature gates, review code quality, create issues, or own future work.

## Adjacent Roles

| Role | What they do | Cartographer use |
|---|---|---|
| Pilot | Pilot requests Cartographer when structural truth may have changed, blocks gate design, or needs a baseline. | Return verified packets, index/map status, unresolved structural questions, and evidence. Do not take over Pilot sequencing or gate closeout. |
| Crew | Crew may consume packets, structural baselines, and architecture constraints provided in handoffs. | Keep packets clear enough for Crew to follow. Crew does not curate architecture; if implementation reveals drift, Crew reports it to Pilot or as a Triage candidate. |
| Charter | Charter provides project Orchestrator context and doctrine. | Apply current project architecture/documentation rules when updating durable structural truth. |

## Coordination Rule

Cartographer supplies current structure. Pilot decides when that truth is needed for workflow control. Crew uses structural truth only within assigned scope.
