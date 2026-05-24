---
name: constellation-workbench
description: Use when non-trivial work needs local todos, workflow artifacts, evidence, closeout, or archive.
---

# Constellation Workbench

## Purpose

Manage temporary, recoverable workflow state. `.agent-work/` is not durable project truth. Workbench owns artifact hygiene, not semantic workflow decisions.

## Layout

```text
.agent-work/
  <work-id>/
    LOCAL_TODO.md
    CONDUCTOR_CHECKLIST.md
    GATED_PLAN.md
    crew-handoffs/
    evidence/
    triage-candidates/

  archive/
    <date>-<work-id>/
      ...
```

Rules:

- Work IDs: `issue-123-slug`, `pr-45-slug`, or `YYYYMMDD-slug`; lowercase, stable, hyphen-separated.
- Start every non-trivial task with `LOCAL_TODO.md` using `templates/LOCAL_TODO.template.md`.
- The todo answers: task, why, done, remaining, blockers, and next step if interrupted.
- Update before real work, after completed steps/gates, when blocked or scope changes, and before handoff/final report.
- Keep todo updates operational, not diaristic.
- Archive semantically closed workflows only; blocked/waiting work stays active.
- Do not read archives unless the user points to them.
- Promote durable truth to docs. Package future work as Triage candidates or issue-ready recommendations by project context.

## Closeout

A workflow is closed when todo is current, evidence captured, durable truth promoted, future work packaged, reconciliation done/skipped with reason, and artifact closeout is complete or explicitly pending/skipped with reason.

Closeout compression: before archiving, delete or condense redundant workflow prose when durable truth or routed Triage recommendations exist elsewhere.
