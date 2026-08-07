# Crash-resume state note — issue-99

Rewrite this **before** launching any detached or multi-hour process, and again
before **each** new detach (the PID changes every time). If this session dies,
a fresh agent resumes from exactly these five lines — no forensics.

The engine enforces the floor: the spine `execute` step has a `command`
precondition (`verify_state_note.py`) that refuses to enter the detach-heavy
phase until every field below is filled. Keeping it current across detaches is
your discipline; the engine only guarantees the first one exists.

- **step:** execute · gate g1-review (reviewer crew dispatched, external backend)
- **slug:** issue-99, branch constellation/issue-99, worktree C:\Programs\constellation-skills
- **next command:** py scripts/recover_crews.py issue-99  (then resume the flagged crew or relaunch via run_crew.py --backend external; spine at .agent-work/issue-99/spine.json, session-id commander-e0e54137)
- **pid:** none — foreground (external-backend Agent-tool dispatch)
- **expected artifact:** .agent-work/issue-99/crew-handoffs/g1-review/REVIEW_RESULT.md

_Updated: 2026-07-09T07:20:00Z_
