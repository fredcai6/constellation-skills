---
name: constellation-workbench
description: Use when work needs local todos, workflow artifacts, evidence, closeout, archive, or to drive a gated/survey checklist through the engine.
---

# Constellation Workbench

Manage recoverable workflow state. `.agent-work/` is not durable project truth. Workbench owns clear workflow managemetn, not semantic decisions.

Compliance/engine-drive rule: inherited — see `references/global-everyone.md` (it binds every role whose checklist Workbench drives).

## Layout

```text
.agent-work/
  AGENT_FEEDBACK.md              # unified run retrospective; persists across work-ids, never archived

  <work-id>/                     # one work-id holds the whole tree
    <checklist>.json             # spine.json, interrogation.json, execute.json, g1-review.json, ...
    crew-handoffs/
    evidence/
    triage-candidates/

  archive/
    <date>-<work-id>/
      <complete work-id package>
```

`AGENT_FEEDBACK.md` is workflow-improvement signal, not project truth: Commander appends one entry per run at its `feedback` step (template `templates/AGENT_FEEDBACK.template.md`). It lives at the agent-work root, accumulates across runs, and is never moved into `archive/`.

Work IDs: `issue-123-slug`, `pr-45-slug`, `YYYYMMDD-slug`; lowercase, stable, hyphen-separated. Prefer `.agent-work/templates/<template-name>`; fall back to bundled `templates/<template-name>`.

## Controller

Each agent drives a JSON checklist via the engine. A role's own template is its controller; `DEFAULT.template.json` covers ad-hoc work. Delegation is by reference (`child_checklist`), so the one work-id holds the whole tree.

## Checklist engine

Drive a controller one step at a time with the absolute path to this installed skill's bundled `scripts/checklist_engine.py` (canonical JSON state). Do not run `scripts/checklist_engine.py` relative to the target repo unless that repo vendors the script. Two types: `gated` (ordered execution; failure blocks) and `survey` (verification/inquiry; visit all, append, never block, consolidate). The engine enforces ordering, evidence shape, the rework cap, and the consolidation guard; it never judges quality. Obey its refusals as the next instruction. See `references/checklist-engine.md`.

## Closeout

Closed = controller current, evidence captured, durable truth promoted, future work packaged, reconciliation done/skipped with reason, artifact closeout complete or explained.

Templates: `templates/DEFAULT.template.json`, `templates/WORKFLOW_CLOSEOUT.template.md`, `templates/AGENT_FEEDBACK.template.md`. References: `references/checklist-engine.md`, `references/status-model.md`.
