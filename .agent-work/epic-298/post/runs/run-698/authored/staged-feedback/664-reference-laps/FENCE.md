# FENCE — 664-reference-laps feedback staging

**Authority:** LAUNCH ORDER — #664 (manifest E), epic #659 Wave 2 (cmdr-664, delegated).
Copy at `C:/Programs/f1Brainz/.agent-work/epic-659/LAUNCH_ORDER-664.md`.

**Cited clause (Constraints & hygiene):** "Do NOT commit any `.agent-work/` path on the
mission branch. Stage the feedback trio (AGENT_FEEDBACK + lessons-delta.json +
CONSTELLATION_FEEDBACK) under `.agent-work/staged-feedback/664-reference-laps/` with a
`FENCE.md` citing this launch order; satisfy your feedback/archive gate against that staging
dir."

**Why staged, not written to the shared root:** this is a delegated Wave-2 run in a fenced
worktree; writing the shared `.agent-work/AGENT_FEEDBACK.md` / `LESSONS.md` /
`CONSTELLATION_FEEDBACK.md` would clobber canonical fleet state from sibling ships
(lesson:shared-files-not-on-mission-branch). The Admiral harvests this trio into the shared
durable root and applies `lessons-delta.json` centrally before sweeping this worktree.

**Trio present in this directory:**
- `AGENT_FEEDBACK.md` — the run retrospective (mentions work-id 664-reference-laps).
- `lessons-delta.json` — structured ops (tick=true; 7 confirms + 1 mention).
- `CONSTELLATION_FEEDBACK.md` — staged exports (engine-artifact-attest,
  from-child-refuses-on-gated-checklist, delegated-commander-foreground-poll corroboration).
- `FENCE.md` — this file.
