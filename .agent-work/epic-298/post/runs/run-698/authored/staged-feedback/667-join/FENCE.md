# FENCE — 667-join feedback staging

**Authority:** LAUNCH ORDER — #667 (manifest H), epic #659 Wave 4a (cmdr-667, delegated).
Copy at `C:/Programs/f1Brainz/.agent-work/epic-659/LAUNCH_ORDER-667.md`.

**Cited clause (Constraints & hygiene):** "Stage the feedback trio (AGENT_FEEDBACK +
lessons-delta.json + CONSTELLATION_FEEDBACK) under `.agent-work/staged-feedback/667-join/`
with a `FENCE.md` citing this launch order; satisfy your feedback/archive gate against that
staging dir. Do NOT commit any `.agent-work/` path on the branch."

**Why staged, not written to the shared root:** delegated Wave-4a run in a fenced worktree;
writing the shared `.agent-work/AGENT_FEEDBACK.md` / `LESSONS.md` / `CONSTELLATION_FEEDBACK.md`
would clobber canonical fleet state from sibling ships (lesson:shared-files-not-on-mission-branch).
The Admiral harvests this trio into the shared durable root and applies `lessons-delta.json`
centrally before sweeping this worktree.

**Trio present in this directory:**
- `AGENT_FEEDBACK.md` — the run retrospective (mentions work-id 667-join).
- `lessons-delta.json` — structured ops (tick=true; confirms).
- `CONSTELLATION_FEEDBACK.md` — upstream export(s) for recurring constellation debt.
