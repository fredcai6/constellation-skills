# FENCE — 671-reconcile

This run was a **fenced delegated commander** under Admiral LAUNCH_ORDER-671
(epic #659 Wave 5b, `C:/Programs/f1Brainz/.agent-work/epic-659/LAUNCH_ORDER-671.md`).

The launch order fences this run to **doc/map work only** and names the feedback
trio staging location explicitly:
> "Feedback trio under `.agent-work/staged-feedback/671-reconcile/` + FENCE.md."

`durable_root()` resolved to the WORKTREE (not the main checkout) because an active
Admiral epic-lease `spine.json` exists in the main checkout — the fencing exception
fired for real (matching `lesson:shared-files-not-on-mission-branch`). The durable
`.agent-work/AGENT_FEEDBACK.md` / `LESSONS.md` / `CONSTELLATION_FEEDBACK.md` were
therefore NOT written or committed on the mission branch; the trio is staged here
for the Admiral to harvest into the shared durable root before sweeping this worktree
(`lesson:harvest-collected-not-verified-merged`).

Staged trio:
- `AGENT_FEEDBACK.md` — this run's retrospective entry.
- `lessons-delta.json` — tick + confirm ops (also at `.agent-work/671-reconcile/lessons-delta.json`).
- `CONSTELLATION_FEEDBACK.md` — constellation exports (none new this run; see file).

No shared playbook file was applied to the worktree copy (c2 `verify_lessons_applied`
was already clear — no ripe lesson pending); the Admiral applies the delta centrally.
