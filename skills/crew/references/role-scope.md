# Crew Role Scope

Crew only needs local workflow recovery plus the handoff, Crew context, and any provided structural baseline.

## Local Workflow State

| Producer | Artifact/interface | Consumer | Contract |
|---|---|---|---|
| Workbench | `.agent-work/<work-id>/LOCAL_TODO.md` | Crew | Local Todo indexes the active controller and recovery state. It is not durable project truth. |
| Role skills | role-specific checklist templates | Active role | Role-specific checklist is the execution controller. Workbench does not own role-specific checklist templates. |

## Crew Boundary

Use `LOCAL_TODO.md` only to recover current work state and find the active controller/handoff. Do not duplicate the role checklist. Do not route, create issues, close gates, or expand scope. Return out-of-scope observations to Pilot.
