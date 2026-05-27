# Crew Role Scope

Crew only needs local workflow recovery plus the handoff, Crew context, and any provided structural baseline.

## Local Workflow State

| Producer | Artifact/interface | Consumer | Contract |
|---|---|---|---|
| Workbench | `.agent-work/<work-id>/DEFAULT_CHECKLIST.md` | Crew | Default Checklist is the controller when no role-specific checklist exists. Optional for one-shot Crew work; used for multi-step recovery. Not durable project truth. |
| Role skills | role-specific checklist templates | Active role | Role-specific checklist is the execution controller when role ships one. Workbench does not own role-specific checklist templates. |

## Crew Boundary

Use `DEFAULT_CHECKLIST.md` only to recover current work state when Crew work spans multiple steps. Do not route, create issues, close gates, or expand scope. Return out-of-scope observations to Pilot.
