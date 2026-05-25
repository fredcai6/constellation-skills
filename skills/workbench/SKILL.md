---
name: constellation-workbench
description: Use when non-trivial work needs local todos, workflow artifacts, evidence, closeout, or archive.
---

# Constellation Workbench

Manage temporary, recoverable workflow state. `.agent-work/` is not durable project truth. Workbench owns artifact hygiene, not semantic workflow decisions.

## Layout

```text
.agent-work/
  <work-id>/
    LOCAL_TODO.md
    PILOT_CHECKLIST.md
    GATED_PLAN.md
    crew-handoffs/
    evidence/
    triage-candidates/

  archive/
    <date>-<work-id>/
      ...
```

Rules: work IDs `issue-123-slug`, `pr-45-slug`, or `YYYYMMDD-slug`; lowercase, stable, hyphen-separated. Start every non-trivial task with `LOCAL_TODO.md`. Prefer `.agent_work/templates/<template-name>`; fall back to bundled `templates/<template-name>`.

If a role-specific checklist exists, copy that controller template too. It is the execution controller; Local Todo indexes the active controller and recovery state. Do not duplicate the role checklist. Keep controller steps checked (`[x]`) or statused as work happens, with execution notes after each step/gate/blocker/scope change and before handoff/final.

Archive only semantically closed workflows; blocked/waiting stays active. Do not read archives unless user points there. Promote durable truth to docs. Package future work as Triage candidates or issue-ready recommendations by project context.

## Closeout

Closed = todo current, evidence captured, durable truth promoted, future work packaged, reconciliation done/skipped with reason, artifact closeout complete or pending/skipped with reason.

Templates: `templates/LOCAL_TODO.template.md`, `templates/WORKFLOW_CLOSEOUT.template.md`.
