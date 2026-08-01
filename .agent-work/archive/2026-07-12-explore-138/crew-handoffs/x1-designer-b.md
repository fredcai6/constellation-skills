# x1 designer B — constraint: hook-carried (harness hooks, engine responses unchanged)

Read `.agent-work/explore-138/crew-handoffs/x1-shared-core.md` FIRST — it holds the question, ground
truth, hard constraints, and deliverable shape. This file only assigns your constraint and result path.

## Your named constraint

**Hook-carried.** Claude Code hooks are your ONLY new channel — engine response strings stay exactly as
they are today. Design the project-local hook suite (`.claude/settings.json` + hook scripts, plausibly
shipped/installed by the workbench skill):

- `SessionStart` (source `compact`, and consider `resume`): re-inject engine state — "mid-spine at
  step X, N steps from terminal, next imperative Y" — sourced live from `checklist_engine.py current`.
- `Stop` hook: when a claimed spine is mid-flight, refuse the turn-end and hand back the next
  imperative. MUST include the escape hatch (engine `block`/`waive` recognized as honest stops; a
  bounded nudge counter, e.g. 3 refusals then allow stop with a loud marker).
- Any other hook events you judge load-bearing (PreCompact, SessionStart-startup for the entry
  ritual) — justify each.

Design the discovery problem: how does a generic hook find WHICH spine file is active for this session
(multiple work areas, worktrees)? And the dependency: hooks-for-subagents is being verified by a
parallel excursion — state your fallback if subagents don't inherit hooks.

## Result path (write the design doc here)

`C:/Programs/constellation-skills/.agent-work/explore-138/evidence/x1-designer-b.md`
