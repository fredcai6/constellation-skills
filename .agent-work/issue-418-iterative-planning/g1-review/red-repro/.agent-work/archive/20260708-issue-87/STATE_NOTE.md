# Crash-resume state note — issue-87

Rewrite this **before** launching any detached or multi-hour process, and again
before **each** new detach (the PID changes every time). If this session dies,
a fresh agent resumes from exactly these five lines — no forensics.

The engine enforces the floor: the spine `execute` step has a `command`
precondition (`verify_state_note.py`) that refuses to enter the detach-heavy
phase until every field below is filled. Keeping it current across detaches is
your discipline; the engine only guarantees the first one exists.

- **step:** execute · gate g1-implement (about to dispatch implementer crew)
- **slug:** issue-87 · branch constellation/issue-87 · worktree C:/Programs/constellation-skills (main checkout)
- **next command:** python C:/Users/fredc/.claude/skills/constellation-commander/scripts/recover_crews.py issue-87 (then resume or relaunch per its report)
- **pid:** none — foreground (run_crew.py is blocking)
- **expected artifact:** .agent-work/issue-87/crew-handoffs/g1-implement/IMPLEMENTER_RESULT.md

_Updated: 2026-07-08T00:00:00 (plan approved, entering execute)_
