# Crash-resume state note — cleanup-b-context-identity

- **step:** execute · gate g1-implement (dispatching the implementer crew)
- **slug:** cleanup-b-context-identity · branch `cleanup/b-context-identity` · worktree `/home/tommy/projects/constellation-skills/.worktrees/cleanup-b-context-identity`
- **next command:** `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py /home/tommy/.claude/skills/constellation-workbench/scripts/checklist_engine.py --file .agent-work/cleanup-b-context-identity/execute.json current` — then, if no crew is running, `py /home/tommy/.claude/skills/constellation-commander/scripts/recover_crews.py cleanup-b-context-identity` before any relaunch
- **pid:** none — foreground; crews are launched through `run_crew.py`, whose durable registry at `.agent-work/cleanup-b-context-identity/crew-runs.json` holds each crew's own PID
- **expected artifact:** `.agent-work/cleanup-b-context-identity/crew-handoffs/g1-implementer-result.md` (and, for the plan-step critic, `crew-handoffs/plan-critic-result.md`)

_Updated: 2026-08-16T12:45:00Z_
