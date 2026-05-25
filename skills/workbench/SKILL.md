---
name: constellation-workbench
description: Use when work needs local todos, workflow artifacts, evidence, closeout, or archive.
---

# Constellation Workbench

Manage recoverable workflow state. `.agent-work/` is not durable project truth. Workbench owns artifact hygiene, not semantic decisions.

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
      <complete work-id package>
```

Rules: work IDs `issue-123-slug`, `pr-45-slug`, or `YYYYMMDD-slug`; lowercase, stable, hyphen-separated. Start with `LOCAL_TODO.md`. Prefer `.agent_work/templates/<template-name>`; fall back to bundled `templates/<template-name>`.

If a role-specific checklist exists, copy it too. It is the execution controller; Local Todo indexes the active controller and recovery state. Do not duplicate the role checklist. Keep controller steps checked (`[x]`) or statused, with notes after steps/gates/blockers and before handoff/final.

Archive only semantically closed workflows; blocked/waiting stays active. Role closeout templates define package movement. Do not read archives unless user points there. Promote durable truth to docs; package future work by project context.

## Closeout

Closed = todo current, evidence captured, durable truth promoted, future work packaged, reconciliation done/skipped with reason, artifact closeout complete or explained.

Templates: `templates/LOCAL_TODO.template.md`, `templates/WORKFLOW_CLOSEOUT.template.md`.
