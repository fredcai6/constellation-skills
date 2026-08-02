# Crash-resume state note — cmdr-504

Rewrite this **before** launching any detached or multi-hour process, and again
before **each** new detach (the PID changes every time). If this session dies,
a fresh agent resumes from exactly these five lines — no forensics.

The engine enforces the floor: the spine `execute` step has a `command`
precondition (`verify_state_note.py`) that refuses to enter the detach-heavy
phase until every field below is filled. Keeping it current across detaches is
your discipline; the engine only guarantees the first one exists.

- **step:** execute · gate g1-integrate (advance running in background, pytest in progress)
- **slug:** cmdr-504 / cleanup/504-split-smoother / C:/Programs/f1Brainz-worktrees/509-504
- **next command:** py C:/Users/fredc/.claude/skills/constellation-commander/scripts/checklist_engine.py --file ".agent-work/cmdr-504/execute.json" current --session-id cmdr-504-session-01 (then advance execute.json and commit if g1-integrate complete)
- **pid:** none — background task b61okmxyi running advance g1-integrate
- **expected artifact:** .agent-work/cmdr-504/execute.json g1-integrate complete; g1-reviewer-result.md APPROVE verdict

_Updated: 2026-06-27T19:45:00Z_
