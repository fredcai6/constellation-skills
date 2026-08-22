# Crash-resume state note — 569

Rewrite this **before** launching any detached or multi-hour process, and again
before **each** new detach (the PID changes every time). If this session dies,
a fresh agent resumes from exactly these five lines — no forensics.

- **step:** execute · wave 1 prelaunch (delivery guarantee + verdict mechanism)
- **slug:** work-id `569`, epic branch `main` (admiral drives from the main checkout at /home/tommy/projects/constellation-skills); wave-1 commander worktrees at ../569-w1-wiring (branch epic-569/w1-wiring) and ../569-w1-verdict (branch epic-569/w1-verdict)
- **next command:** `python3 /home/tommy/.claude/skills/constellation-admiral/scripts/verify_iterative_role_artifacts.py admiral-prelaunch --work-id 569` — a zero exit clears wave-1 dispatch; then re-read .agent-work/569/ADMIRAL_LOG.md and .agent-work/569/LATITUDE_CONTRACT.md and dispatch the two wave-1 commanders from .agent-work/569/crew-handoffs/
- **pid:** none — foreground; commanders dispatch in-harness via the Agent tool
- **expected artifact:** .agent-work/569/crew-handoffs/w1-wiring-RESULT.md and w1-verdict-RESULT.md, plus two merged PRs on main

_Updated: 2026-08-22T12:30:00+00:00_
