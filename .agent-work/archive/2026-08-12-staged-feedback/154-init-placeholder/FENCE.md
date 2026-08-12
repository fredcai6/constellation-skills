# Fence citation -- 154-init-placeholder

This delegated run is fenced off the main checkout's durable `.agent-work/` per its Admiral launch order:

- **Launch order:** `C:/Programs/constellation-skills/.agent-work/epic-198-burndown/launch-orders/W2-154-init-placeholder.md`
- **Fence (File Ownership):** scripts/init_work_area.py, scripts/stage_feedback.py, and their test files under tests/ (sole writer this wave)
- **Return Shape:** implement/test/open PR (no merge); write report to .agent-work/epic-198-burndown/wave-2/W2-154-REPORT.md in the MAIN checkout; dogfood stage_feedback.py for the fenced trio

Per the delegated-commander "Fenced feedback/archive closeout -- stage, do not waive" doctrine, the durable-root write is impossible from this worktree, so the feedback trio is staged here instead of waived:

- `AGENT_FEEDBACK.md` -- this run's retrospective entry
- `lessons-delta.json` -- tick + lesson ops
- `CONSTELLATION_FEEDBACK.md` -- constellation export (or confirmed-empty)

The Admiral harvests this trio into the shared durable `.agent-work/` root before sweeping this worktree.
