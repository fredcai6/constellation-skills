# Crash-resume state note — <work-id>

Rewrite this **before** launching any detached or multi-hour process, and again
before **each** new detach (the PID changes every time). If this session dies,
a fresh agent resumes from exactly these five lines — no forensics.

The engine enforces the floor: the spine `execute` step has a `command`
precondition (`verify_state_note.py`) that refuses to enter the detach-heavy
phase until every field below is filled. Keeping it current across detaches is
your discipline; the engine only guarantees the first one exists.

- **step:** <which spine/gate step you are on, e.g. execute · gate g2-integrate>
- **slug:** <work-id, branch, and worktree path>
- **next command:** <the exact command a fresh agent runs to resume>
- **pid:** <PID of the detached process, or "none — foreground">
- **expected artifact:** <the output file whose existence signals completion>

_Updated: <iso8601 timestamp of this rewrite>_
