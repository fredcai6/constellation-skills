---
name: constellation-workbench
description: Use when work needs the shared workflow templates, or a pointer to the checklist engine's CLI fallback and MCP door -- the engine's verbs and mechanism are taught by the door's own tool descriptions, not by this skill.
---

# Constellation Workbench

Retired as a taught procedure (issue #565): the MCP door's own tool descriptions now teach the
checklist engine's verbs, evidence shape, and mechanism directly, so this skill no longer
restates them. What remains: the four shared templates every role's checklist instantiates
from (`templates/`), and the one pointer below, which stays load-bearing because other skills
and two independent test suites cite it directly.

## Checklist engine

Drive a controller one step at a time — by default via the MCP door's `spine_status`/`spine_lease`/`spine_start`/`spine_advance`/`spine_evidence`/`spine_halt`/`spine_survey_result` tools when this agent owns the process's bound spine (see `references/checklist-engine.md` — MCP door); CLI fallback, always available and the only path for an in-session dispatched crew member driving its own plan or survey: the absolute path to this installed skill's bundled `scripts/checklist_engine.py` (canonical JSON state). Do not run `scripts/checklist_engine.py` relative to the target repo unless that repo vendors the script. See `references/checklist-engine.md`.

Templates: `templates/DEFAULT.template.json`, `templates/WORKFLOW_CLOSEOUT.template.md`, `templates/STATE_NOTE.template.md`, `templates/CONSTELLATION_FEEDBACK.template.md`. References: `references/checklist-engine.md`, `references/status-model.md`.
