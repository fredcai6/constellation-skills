# Crash-resume state note — euler-001-20260710

Rewrite this **before** launching any detached or multi-hour process, and again
before **each** new detach (the PID changes every time). If this session dies,
a fresh agent resumes from exactly these five lines — no forensics.

The engine enforces the floor: the spine `execute` step has a `command`
precondition (`verify_state_note.py`) that refuses to enter the detach-heavy
phase until every field below is filled. Keeping it current across detaches is
your discipline; the engine only guarantees the first one exists.

- **step:** execute · starting gate g1-implement
- **slug:** euler-001-20260710, workspace root, no branch yet
- **next command:** py .claude/skills/constellation-workbench/scripts/checklist_engine.py --file .agent-work/euler-001-20260710/execute.json current
- **pid:** none — foreground crew dispatch
- **expected artifact:** .agent-work/euler-001-20260710/crew-g1-implement-implementer/IMPLEMENTER_RESULT.md

_Updated: 2026-07-10T18:39:40Z_
