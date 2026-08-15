# Crash-resume state note — episode-guard-at-write

Rewrite this **before** launching any detached or multi-hour process, and again
before **each** new detach (the PID changes every time). If this session dies,
a fresh agent resumes from exactly these five lines — no forensics.

The engine enforces the floor: the spine `execute` step has a `command`
precondition (`verify_state_note.py`) that refuses to enter the detach-heavy
phase until every field below is filled. Keeping it current across detaches is
your discipline; the engine only guarantees the first one exists.

- **step:** execute · gate g1-implement (closing c5, re-run of clean-env suite after map/INDEX.md regen)
- **slug:** episode-guard-at-write · branch fix/episode-guard-at-write · worktree /home/tommy/projects/constellation-skills/.worktrees/episode-guard-at-write
- **next command:** `tail -25 /tmp/egaw2-suite2.log` — first run (egaw2-suite.log) was 3039 passed, 6 skipped, 1146 subtests, 1 failed (map/INDEX.md stale); map was regenerated via `python -m scripts.code_map build --root .` (uncommitted). This second run must show 0 failed before attaching c5 evidence and advancing g1-implement, then execute, then committing the map.
- **pid:** 114524 (clean-env cache-clean `python -m pytest -q`, logging to /tmp/egaw2-suite2.log)
- **expected artifact:** /tmp/egaw2-suite2.log containing a line matching `[0-9]+ (passed|failed)`

_Updated: 2026-08-15T22:40:00Z_
