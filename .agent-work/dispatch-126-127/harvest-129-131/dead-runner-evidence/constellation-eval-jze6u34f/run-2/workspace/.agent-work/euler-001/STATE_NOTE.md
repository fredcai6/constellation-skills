# Crash-resume state note — euler-001

Rewrite this **before** launching any detached or multi-hour process, and again
before **each** new detach (the PID changes every time). If this session dies,
a fresh agent resumes from exactly these five lines — no forensics.

The engine enforces the floor: the spine `execute` step has a `command`
precondition (`verify_state_note.py`) that refuses to enter the detach-heavy
phase until every field below is filled. Keeping it current across detaches is
your discipline; the engine only guarantees the first one exists.

- **step:** execute · driving execute.json gate by gate
- **slug:** euler-001, branch main, worktree .
- **next command:** py C:/Users/fredc/AppData/Local/Temp/constellation-eval-jze6u34f/skills/constellation-workbench/scripts/checklist_engine.py --file .agent-work/euler-001/execute.json current
- **pid:** none — foreground
- **expected artifact:** .agent-work/euler-001/IMPLEMENTER_RESULT.md and REVIEW_RESULT.md for g1

_Updated: 2026-07-10T13:45:00Z_
