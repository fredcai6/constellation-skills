# Crash-resume state note — epic-567-door/cmdr-g

- **step:** execute · gate g1-implement (about to dispatch implementer crew)
- **slug:** epic-567-door/cmdr-g · branch `feat/567-g-closeout-lease` · worktree `/home/tommy/projects/constellation-skills/.worktrees/567-g-closeout-lease`
- **next command:** `cd /home/tommy/projects/constellation-skills/.worktrees/567-g-closeout-lease && py /home/tommy/.claude/skills/constellation-commander/scripts/recover_crews.py epic-567-door/cmdr-g` then `PYTHONIOENCODING=utf-8 py scripts/checklist_engine.py --file .agent-work/epic-567-door/cmdr-g/execute.json current`
- **pid:** none — foreground
- **expected artifact:** `.agent-work/epic-567-door/cmdr-g/crew-handoffs/g1-implementer-result.md`

_Updated: 2026-08-17T05:50:00+00:00_

## Resume context (beyond the five lines)

Commander spine `.agent-work/epic-567-door/cmdr-g/spine.json`, lease
`cmdr-567-g#main`, driven via CLI fallback (the MCP door is bound to no spine
this session — it refused `spine_status` at start, so it can never reach the
Admiral's live epic spine). Steps init→plan are complete; `execute` is in
progress. Child plan `execute.json` holds the 3 crew gates. Frozen plan is
candidate B with all six cold-critic findings folded in — see
`PLAN_ALTERNATIVES.md` §Cold-critic disposition and `PLAN_CRITIC.md`.

Fences: never edit `scripts/checklist_engine.py`, `scripts/mcp_spine_server.py`
(lane A's this wave) or `scripts/hooks/spine_rail.py` (library-call only).
Never run new code against a live spine — fixtures under tmp_path only.
