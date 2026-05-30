---
name: constellation-workbench
description: Use when work needs local todos, workflow artifacts, evidence, closeout, archive, or to drive a gated/survey checklist through the engine.
---

# Constellation Workbench

Manage recoverable workflow state. `.agent-work/` is not durable project truth. Workbench owns clear workflow managemetn, not semantic decisions.

Mandatory, not advisory: once a role skill is loaded, drive its checklist to completion through the engine and dispatch each step it names; do not improvise.

## Layout

```text
.agent-work/
  <work-id>/                     # one work-id holds the whole tree
    <checklist>.json             # spine.json, interrogation.json, execute.json, g1-review.json, ...
    crew-handoffs/
    evidence/
    triage-candidates/

  archive/
    <date>-<work-id>/
      <complete work-id package>
```

Work IDs: `issue-123-slug`, `pr-45-slug`, `YYYYMMDD-slug`; lowercase, stable, hyphen-separated. Prefer `.agent-work/templates/<template-name>`; fall back to bundled `templates/<template-name>`.

## Controller

Each agent drives a JSON checklist via the engine. A role's own template is its controller; `DEFAULT.template.json` covers ad-hoc work. Delegation is by reference (`child_checklist`), so the one work-id holds the whole tree.

## Checklist engine

Drive a controller one step at a time with the absolute path to this installed skill's bundled `scripts/checklist_engine.py` (canonical JSON state). Do not run `scripts/checklist_engine.py` relative to the target repo unless that repo vendors the script. Two types: `gated` (ordered execution; failure blocks) and `survey` (verification/inquiry; visit all, append, never block, consolidate). The engine enforces ordering, evidence shape, the rework cap, and the consolidation guard; it never judges quality. Obey its refusals as the next instruction. See `references/checklist-engine.md`.

## Closeout

Closed = controller current, evidence captured, durable truth promoted, future work packaged, reconciliation done/skipped with reason, artifact closeout complete or explained.

Templates: `templates/DEFAULT.template.json`, `templates/WORKFLOW_CLOSEOUT.template.md`. References: `references/checklist-engine.md`, `references/status-model.md`.
