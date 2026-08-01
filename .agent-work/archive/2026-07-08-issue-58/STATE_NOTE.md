# Crash-resume state note — issue-58

Rewrite this **before** launching any detached or multi-hour process, and again
before **each** new detach (the PID changes every time). If this session dies,
a fresh agent resumes from exactly these five lines — no forensics.

The engine enforces the floor: the spine `execute` step has a `command`
precondition (`verify_state_note.py`) that refuses to enter the detach-heavy
phase until every field below is filled. Keeping it current across detaches is
your discipline; the engine only guarantees the first one exists.

- **step:** execute · g5-implement complete (commit 2c8074d; FULL SUITE GREEN 424 passed 0 failed — epic exit criterion met, waiver window closed); g5-review in-progress — reviewer crew attempt-1 dispatched (external)
- **slug:** issue-58 · branch constellation/issue-58 · worktree C:\Programs\constellation-skills
- **next command:** python scripts/recover_crews.py issue-58   (then resume or verify per its report; engine: python scripts/checklist_engine.py --file .agent-work/issue-58/execute.json current)
- **pid:** harness background task (run_crew.py foreground child of this session) — registry entry in .agent-work/issue-58/crew-runs.json is authoritative
- **expected artifact:** .agent-work/issue-58/crew-handoffs/g5-review/REVIEW_RESULT.md

_Updated: 2026-07-08T21:45:00-07:00_
