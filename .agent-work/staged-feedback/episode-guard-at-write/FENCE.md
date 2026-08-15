# Fence citation — episode-guard-at-write

Governing order: `.agent-work/episode-guard-at-write/LAUNCH_ORDER-2.md` (frozen, admiral-post-568).

This run is not explicitly fenced from writing the main checkout by LAUNCH_ORDER-2 (its only stated
fence is "fenced from merging" the PR). The archive gate's own `c4` postcondition, however,
unconditionally deny-globs `.agent-work/CONSTELLATION_FEEDBACK.md` in its git-change-policy check, so a
direct commit of an edit to that file structurally fails c4 regardless of launch-order fencing. Per the
delegated-commander skill's fenced feedback/archive closeout clause, the gate is not waived for this;
the export is staged here instead, and a direct edit that was made to the tracked file during the
feedback step was reverted (`git restore .agent-work/CONSTELLATION_FEEDBACK.md`) before this run's
archive diff was staged.

Episodes are unaffected and are committed inside this worktree under `episodes/` (4 for this run,
`episode-guard-at-write-001` through `-004`: `-001` from attempt-1's implementation work, `-002`
through `-004` from this attempt's own plan.c6 escalation, stale-map catch, and REPLAN_INPUT ceremony),
written through `scripts/apply_episode_delta.py --store-root episodes` and proved by
`scripts/verify_episode_captured.py` (exit 0).

Admiral: harvest this directory before sweeping the worktree.
