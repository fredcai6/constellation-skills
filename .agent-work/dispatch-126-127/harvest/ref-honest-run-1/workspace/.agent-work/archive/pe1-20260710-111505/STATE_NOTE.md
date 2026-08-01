# Crash-resume state note — pe1-20260710-111505

Rewrite this **before** launching any detached or multi-hour process, and again
before **each** new detach (the PID changes every time). If this session dies,
a fresh agent resumes from exactly these five lines — no forensics.

The engine enforces the floor: the spine `execute` step has a `command`
precondition (`verify_state_note.py`) that refuses to enter the detach-heavy
phase until every field below is filled. Keeping it current across detaches is
your discipline; the engine only guarantees the first one exists.

- **step:** execute · e0-context
- **slug:** pe1-20260710-111505, main branch, workspace root
- **next command:** python .claude/skills/constellation-workbench/scripts/checklist_engine.py --file .agent-work/pe1-20260710-111505/execute.json current
- **pid:** none — foreground
- **expected artifact:** .agent-work/pe1-20260710-111505/execute.json (driven to completion)

_Updated: 2026-07-10T18:15:30Z_
