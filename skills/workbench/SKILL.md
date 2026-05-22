---
name: constellation-workbench
description: Maintain live recoverable workflow state through local todos, workflow artifacts, closeout, and archive.
---

# Constellation Workbench

## Purpose

Manage temporary workflow state. The workbench is not durable project truth.

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

- Conductor or Cartographer creates and manages work IDs.
- Archive when the workflow closes.
- Do not edit archived workflow artifacts.
- Agents do not read archived artifacts unless the user explicitly points to them.
- Anything future workflows should rely on must be promoted to durable artifacts.

## Local todo rule

Every non-trivial agent task starts with `LOCAL_TODO.md`.

The todo must answer:

- What was the task?
- Why is it being done?
- What is done?
- What remains?
- What is blocking?
- What should the next agent do first if interrupted?

## Update cadence

Update before starting real work, after each completed step/gate, when blocked, when scope changes, before stopping/handoff, and before final report.

Do not update for every tiny action. Keep it operational, not diaristic.

## Closeout

A workflow is closed when local todo is current, evidence is captured, durable truths are promoted, issue-ready recommendations are written if needed, reconciliation is complete or skipped with reason, and the work folder is archived.
