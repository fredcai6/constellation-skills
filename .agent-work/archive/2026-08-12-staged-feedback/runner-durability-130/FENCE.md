# Fence citation — runner-durability-130

This delegated commander run is fenced off the shared/main-checkout durable feedback root.

**Governing launch order:** `.agent-work/epic-198-burndown/launch-orders/W2-130-runner-durability.md`
(Admiral epic-198 burndown, wave 2, issue #130 — runner durability).

**Fence basis:**
- Work executed entirely in the linked worktree `C:/Programs/cs-wt-runner` (branch
  `fix/runner-durability-130`), where `.agent-work/` is gitignored (worktree-local) — the
  durable-root write to the shared `.agent-work/AGENT_FEEDBACK.md` / `LESSONS.md` /
  `CONSTELLATION_FEEDBACK.md` is not reachable from here.
- File ownership in the launch order scopes this run to `scripts/run_skill_eval.py` +
  `tests/test_run_skill_eval.py`; it does not grant writes to the shared feedback root.

Per constellation-commander-delegated doctrine (fenced feedback/archive closeout — stage, do not
waive), the complete worktree-local trio is staged alongside this citation for the Admiral to harvest
into the shared root before sweeping this worktree:
- `AGENT_FEEDBACK.md` — this run's retrospective (mentions work id `runner-durability-130`).
- `lessons-delta.json` — tick + one handoff-scope add (`observe-midprocess-state-not-via-end-output`).
- `CONSTELLATION_FEEDBACK.md` — two non-blocking engine-CLI ergonomics notes.
