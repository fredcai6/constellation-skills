# Triage candidate: `checklist_engine.py`'s own `refusals` counter never sees a door-own rejection

**Found by:** Commander design work (DESIGN_NOTE.md), confirmed by the implementer, work-id
567-e, issue #541.

**What was found:** `scripts/checklist_engine.py` arms and increments a `refusals` counter on
the checklist itself (`cl["refusals"]`), which `scripts/episode_capture.py`'s
`mechanical_fields()` already reads with zero agent effort into any episode's `## Mechanical`
bin. That counter only increments for refusals the ENGINE itself raises (inside
`checklist_engine.main()`). Door-own rejections — an unbound door, a bad argument, the two
`_spine_bind` containment refusals this gate's mission is about — short-circuit in
`scripts/mcp_spine_server.py`'s `_tool_error()` *before* `run_engine()` is ever called, so they
never reach that counter.

**Why it matters:** Any episode captured for a door-own rejection (this gate's new
`_capture_refusal_episode()`) reports a `refusals` count that is honestly read from engine
state but is an undercount by construction — it excludes the very refusal that triggered the
capture, and any other door-own rejections during the same run. This is not a fabrication (the
number IS what the engine currently believes), but it is a real gap between what an episode's
mechanical bin implies and what actually happened.

**Why not fixed here:** `scripts/checklist_engine.py` is fenced to lane H this wave (issue
#567 wave 2). Fixing it means either the engine exposing a new verb/hook the door can call to
bump its own counter, or the door writing to the checklist file directly — the latter would
violate "the engine owns spine.json" (provenance, lease, heartbeats) and is out of the
question. The former is a real engine change, appropriately scoped to whichever lane next owns
`checklist_engine.py`.

**Recommendation:** When `checklist_engine.py` is next open for change, consider a narrow verb
or hook the MCP door can call to register a rejection against the bound checklist's own
`refusals` counter, mirroring how `claim` already arms it. Small, mechanical, but a genuine
engine-surface change, not a script-local one.

**Owner suggestion:** lane H (owns `scripts/checklist_engine.py` this wave), or a standalone
follow-up issue.
