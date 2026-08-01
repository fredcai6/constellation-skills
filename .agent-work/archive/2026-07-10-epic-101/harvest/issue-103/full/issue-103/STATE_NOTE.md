# Crash-resume state note — issue-103

- **step:** execute · about to drive execute.json gate g1-implement (crews dispatched as synchronous Agent-tool subagents, foreground)
- **slug:** issue-103, branch constellation/issue-103, worktree C:/Programs/constellation-wt-103
- **next command:** py scripts/checklist_engine.py --file .agent-work/issue-103/execute.json current  (then resume from the ACTIVE gate; recover crews via py scripts/recover_crews.py issue-103)
- **pid:** none — foreground (no detached process; crews are synchronous in-context Agent-tool subagents)
- **expected artifact:** .agent-work/issue-103/ crew results + green PR; spine.json all steps complete

_Updated: 2026-07-10T03:00:00+00:00_
