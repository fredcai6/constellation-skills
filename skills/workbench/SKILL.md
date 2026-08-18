---
name: constellation-workbench
description: Use when work needs the shared workflow templates, or a pointer to the checklist engine's MCP door -- the engine's verbs and mechanism are taught by the door's own tool descriptions, not by this skill.
---

# Constellation Workbench

Retired as a taught procedure (issue #565): the MCP door's own tool descriptions now teach the
checklist engine's verbs, evidence shape, and mechanism directly, so this skill no longer
restates them. What remains: the four shared templates every role's checklist instantiates
from (`templates/`), and the one pointer below, which stays load-bearing because other skills
and two independent test suites cite it directly.

## Checklist engine

Drive a controller one step at a time — by default via the MCP door's `spine_status`/`spine_lease`/`spine_start`/`spine_advance`/`spine_evidence`/`spine_halt`/`spine_survey_result` tools when this agent owns the process's bound spine (see `references/checklist-engine.md` — MCP door). An in-session dispatched crew member driving its own plan or survey is not that case: one door drives one spine at a time and refuses to rebind while its owner still holds that spine's lease, so the door cannot reach that file at all. That is not a second-best path with a working primary behind it — such a plan or survey is driven by this skill's bundled checklist engine, and by nothing else. See `references/checklist-engine.md`.

Templates: `templates/DEFAULT.template.json`, `templates/WORKFLOW_CLOSEOUT.template.md`, `templates/STATE_NOTE.template.md`, `templates/CONSTELLATION_FEEDBACK.template.md`. References: `references/checklist-engine.md`, `references/status-model.md`.

What a run learned is not kept here. It is recorded as **episodes** under the repo-root `episodes/` directory, written at the Commander's `feedback` step through `scripts/apply_episode_delta.py` — the store's only write path — and never hand-edited. An episode is a record of what happened, not a rule for a later agent to follow.
