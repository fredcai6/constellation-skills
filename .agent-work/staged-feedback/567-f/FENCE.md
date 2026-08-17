# FENCE — why the durable-root feedback export is staged here, not written

`LAUNCH_ORDER.md` (Data Locations) states directly: "The main checkout is
`/home/tommy/projects/constellation-skills` -- readable if you need it, **never**
writable by you." The Admiral's epic lease is active for this wave, so `durable_root()`
would otherwise resolve to the main checkout's `.agent-work/CONSTELLATION_FEEDBACK.md` --
fenced. The export that would normally land there is staged beside this file instead, for
the Admiral to harvest.

**This is a staging, not a waiver.** The `feedback` gate was not waived, and this run's
episodes are unaffected by the fence: `episodes/` is a tracked path inside this worktree, so
all 3 episodes were written through `scripts/apply_episode_delta.py --store-root episodes` --
the only sanctioned write path -- and proved by `verify_episode_captured.py`, exit 0
(`episode capture: 3 episode(s) recorded for run '567-f' in episodes/active`). The commit is
what carries them out.

Per `constellation-commander-delegated`'s own instruction: a `FENCE.md` citation **without**
the staged export still fails the gate, because learning may not be silently dropped. The
export is `CONSTELLATION_FEEDBACK.md` in this directory.
