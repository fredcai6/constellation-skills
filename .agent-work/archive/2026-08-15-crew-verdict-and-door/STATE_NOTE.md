# Crash-resume state note — crew-verdict-and-door

- **step:** execute · gate e0-context (about to start)
- **slug:** crew-verdict-and-door, branch fix/crew-verdict-and-door, worktree /home/tommy/projects/constellation-skills/.worktrees/crew-verdict-and-door
- **next command:** `python scripts/recover_crews.py crew-verdict-and-door`, then drive execute.json gate by gate via the mcp__spine__ engine tools (spine_status/spine_start/spine_evidence/spine_advance) against `.agent-work/crew-verdict-and-door/spine.json`, whose active step is `execute`, and whose child checklist `execute.json` names each gate.
- **pid:** none — foreground (all crew dispatch this run uses the external backend: no spawned child process; each implementer/reviewer runs synchronously in-turn as an Agent-tool subagent)
- **expected artifact:** `.agent-work/crew-verdict-and-door/crew-handoffs/g1-implementer-result.md`, then `g1-reviewer-result.md`, then `g2-implementer-result.md`, then `g2-reviewer-result.md`, in that order; final signal is `spine_status` reporting the `execute` step complete.

_Updated: 2026-08-15T16:52:00Z_
