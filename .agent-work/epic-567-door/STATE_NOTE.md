# Crash-resume state note — epic-567-door

Rewrite this **before** launching any detached or multi-hour process, and again
before **each** new detach (the PID changes every time). If this session dies,
a fresh agent resumes from exactly these five lines — no forensics.

- **step:** execute · wave 1 dispatch (boundary `w1`) — Admiral spine `.agent-work/epic-567-door/spine.json`, step `execute`
- **slug:** epic-567-door · main checkout `/home/tommy/projects/constellation-skills` on branch `main` · lane worktrees under `.worktrees/567-{a,b,c,g}-*` on branches `feat/567-{a,b,c,g}-*`
- **next command:** `py /home/tommy/.claude/skills/constellation-admiral/scripts/checklist_engine.py --file .agent-work/epic-567-door/spine.json current --session-id a4704163-34f0-4c9f-aca6-8d68c189ab36`
- **pid:** none — foreground (Commanders run as in-process Agent-tool subagents, polled inside the Admiral's turn; no OS-detached process)
- **expected artifact:** `<worktree>/RETURN.md` per lane — `.worktrees/567-a-spine-identity/RETURN.md`, `.worktrees/567-b-external-backend/RETURN.md`, `.worktrees/567-c-rail-readability/RETURN.md`, `.worktrees/567-g-closeout-lease/RETURN.md`. The Admiral polls for these inside its turn and copies each into `.agent-work/epic-567-door/results/`.

_Updated: 2026-08-16T05:20:00Z — wave 1 dispatched, four in-process Commanders (no OS-detached PIDs). If this session dies: the four worktrees and their branches survive on disk; adjudicate each from its `RETURN.md` and git state, confirm the original agent dead before launching any continuation into its worktree, and resume the Admiral spine at `execute` via the next-command line above._
