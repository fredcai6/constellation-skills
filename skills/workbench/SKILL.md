---
name: constellation-workbench
description: Maintain recoverable workflow state. Use when non-trivial work needs local todos, evidence, closeout, or archive.
---

# Constellation Workbench

## Purpose

Manage temporary, recoverable workflow state. `.agent-work/` is not durable project truth.

## Layout

```text
.agent-work/
  <work-id>/
    LOCAL_TODO.md
    FRAMING_NOTE.md
    GATED_PLAN.md
    handoffs/
    evidence/
    issue-recommendations/

  archive/
    <date>-<work-id>/
      ...
```

Rules:

- Conductor or Cartographer creates work IDs: `issue-123-slug`, `pr-45-slug`, or `YYYYMMDD-slug`.
- Keep work IDs lowercase, stable, and hyphen-separated; do not rename after handoffs/evidence unless actively misleading.
- Start every non-trivial task with `LOCAL_TODO.md` using `templates/LOCAL_TODO.template.md`.
- The todo answers: task, why, done, remaining, blockers, and next step if interrupted.
- Update before real work, after completed steps/gates, when blocked or scope changes, and before handoff/final report.
- Keep todo updates operational, not diaristic.
- Archive closed workflows; do not edit archived artifacts.
- Do not read archives unless the user points to them.
- Promote anything future workflows rely on to durable docs or the issue tracker.

## Closeout

A workflow is closed when the todo is current, evidence captured, durable truth promoted, future work packaged, reconciliation done/skipped with reason, and the work folder archived.

Closeout compression: before archiving, delete or condense redundant workflow prose when the durable truth or issue-ready recommendation now exists elsewhere.
