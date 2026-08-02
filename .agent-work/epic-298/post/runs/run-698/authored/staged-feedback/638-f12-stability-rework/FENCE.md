# FENCE — staged feedback for 638-f12-stability-rework

This is a **delegated commander run** under the Admiral LAUNCH_ORDER `ShipD-638` (epic #601),
with **no reachable human**. The launch order fences this commander to:
- "Sole writer this wave: verdict `C:/Programs/f1Brainz/.agent-work/epic-601/wave3-638-verdict.md`;
  workbench under your worktree `.agent-work/`."
- Commit only "the modified `src/physics/layer2/*.py`, tests, scripts, and updated rollup evidence
  under `docs/physics/`."

The shared **durable** feedback log lives in the MAIN checkout
(`C:/Programs/f1Brainz/.agent-work/AGENT_FEEDBACK.md` / `LESSONS.md` /
`CONSTELLATION_FEEDBACK.md`), which this run is fenced from writing, and the Commander-spine
archive `git-change-policy` explicitly DENIES committing those files. Per the
`constellation-commander-delegated` doctrine ("Fenced feedback/archive closeout — stage, do not
waive"), the feedback trio is therefore STAGED here for the Admiral to harvest into the shared
root at epic closeout:
- `AGENT_FEEDBACK.md` — this run's retrospective entry.
- `lessons-delta.json` — adjudicated lesson ops (3 confirms + 1 add with bank_reason + tick).
- `CONSTELLATION_FEEDBACK.md` — 2 constellation-scope exports.

`verify_lessons_applied.py --file .agent-work/LESSONS.md` was clear this run (no ripe lesson
awaiting apply-or-defer), so no shared-LESSONS.md write was needed or attempted.
