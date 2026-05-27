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
    <ROLE_CHECKLIST>.md          # if role ships one
    DEFAULT_CHECKLIST.md         # otherwise
    crew-handoffs/
    evidence/
    triage-candidates/

  archive/
    <date>-<work-id>/
      <complete work-id package>
```

Work IDs: `issue-123-slug`, `pr-45-slug`, `YYYYMMDD-slug`; lowercase, stable, hyphen-separated. Prefer `.agent-work/templates/<template-name>`; fall back to bundled `templates/<template-name>`.

## Controller

One controller per work package. Role checklist (`PILOT_CHECKLIST`, `CHARTER_CHECKLIST`, `CARTOGRAPHER_CHECKLIST`) when role ships one; else `DEFAULT_CHECKLIST`. Never both.

Each gate carries goal, criteria, status, evidence/note. Mark `[x]` or status-stamped. Notes after gates/blockers and before handoff/final.

## Archive

Archive only semantically closed workflows; blocked/waiting stays active. Role closeout templates define package movement. Promote durable truth to docs; package future work by project context. Do not read archives unless user points there.

## Closeout

Closed = controller current, evidence captured, durable truth promoted, future work packaged, reconciliation done/skipped with reason, artifact closeout complete or explained.

Templates: `templates/DEFAULT_CHECKLIST.template.md`, `templates/WORKFLOW_CLOSEOUT.template.md`. Reference: `references/status-model.md`.
