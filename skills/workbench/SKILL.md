---
name: constellation-workbench
description: Use when work needs local todos, workflow artifacts, evidence, closeout, archive, or to drive a gated/survey checklist through the engine.
---

# Constellation Workbench

Manage recoverable workflow state. `.agent-work/` is not durable project truth. Workbench owns clear workflow management, not semantic decisions.

Drive every step through the checklist engine and finish its sequence — final `advance`, then `release`, as journaled actions. Work the engine never saw did not happen. Full completion doctrine: `_shared/global-everyone.md`.

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

What a run learned is not kept here. It is recorded as **episodes** under the repo-root `episodes/` directory, written at the Commander's `feedback` step through `scripts/apply_episode_delta.py` — the store's only write path — and never hand-edited. An episode is a record of what happened, not a rule for a later agent to follow.

Work IDs: `issue-123-slug`, `pr-45-slug`, `YYYYMMDD-slug`; lowercase, stable, hyphen-separated. Prefer `.agent-work/templates/<template-name>`; fall back to bundled `templates/<template-name>`.

## Controller

Each agent drives a JSON checklist via the engine. A role's own template is its controller; `DEFAULT.template.json` covers ad-hoc work. Delegation is by reference (`child_checklist`), so the one work-id holds the whole tree.

## Checklist engine

Drive a controller one step at a time — by default via the MCP door's `spine_status`/`spine_lease`/`spine_start`/`spine_advance`/`spine_evidence`/`spine_halt`/`spine_survey_result` tools when this agent owns the process's bound spine (see `references/checklist-engine.md` — MCP door); CLI fallback, always available and the only path for an in-session dispatched crew member driving its own plan or survey: the absolute path to this installed skill's bundled `scripts/checklist_engine.py` (canonical JSON state). Do not run `scripts/checklist_engine.py` relative to the target repo unless that repo vendors the script. Two types: `gated` (ordered execution; failure blocks) and `survey` (verification/inquiry; visit all, append, never block, consolidate). The engine enforces ordering, evidence shape, the rework cap, and the consolidation guard; it never judges quality. Obey its refusals as the next instruction. See `references/checklist-engine.md`.

## Closeout

Closed = controller current, evidence captured, durable truth promoted, future work packaged, reconciliation done/skipped with reason, artifact closeout complete or explained.

Templates: `templates/DEFAULT.template.json`, `templates/WORKFLOW_CLOSEOUT.template.md`, `templates/STATE_NOTE.template.md`, `templates/CONSTELLATION_FEEDBACK.template.md`. References: `references/checklist-engine.md`, `references/status-model.md`.
