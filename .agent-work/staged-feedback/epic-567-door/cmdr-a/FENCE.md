# FENCE — why the durable-root feedback export is staged here, not written

`durable_root()` resolves to **this worktree**, not the main checkout, because the
Admiral's epic lease is active and the main checkout is fenced read-only for that
reason. `LANE_A_LAUNCH_ORDER.md` §Inherited Context states it directly:

> "**`durable_root()` points at your worktree, not the main checkout**, because the
> Admiral's epic lease is active and the main checkout is fenced read-only for that
> reason. Write your work area, triage candidates and feedback export inside **your own
> worktree**. The Admiral harvests before sweeping it."

So the `CONSTELLATION_FEEDBACK.md` export that would normally land at the durable root is
staged beside this file instead, for the Admiral to harvest.

**This is a staging, not a waiver.** The `feedback` gate was not waived and the run's
episodes are unaffected by the fence: `episodes/` is a tracked path inside this worktree,
so all 12 episodes were written through
`scripts/apply_episode_delta.py --store-root episodes` — the only sanctioned write path —
and proved by `verify_episode_captured.py`, exit 0. The commit is what carries them out.

Per `constellation-commander-delegated`'s own instruction: a `FENCE.md` citation
**without** the staged export still fails the gate, because learning may not be silently
dropped. The export is `CONSTELLATION_FEEDBACK.md` in this directory.
