# Admiral note — lane C has landed (2026-08-16)

`LAUNCH_ORDER-2.md` told you lane C had landed nothing yet. That is now out of
date, which is why this file exists rather than an edit to the order.

**On `main` at `df6f951b`:** #599 (`entry_liveness` corroborates the crew
registry's status string) and #549 (`decide_stop` keeps every block but stops
rendering a subordinate's next imperative into an orchestrator's turn). Merged
tree measured at 3089 passed / 7 skipped / 0 failed against a 3069 gate-time
baseline — additions only, no failures.

## What it means for your measurement

#549 removes one **route** into the collision you measured: an orchestrator whose
Stop hook reaches a subordinate's spine. It does **not** remove the mechanism.
`session_view`'s per-agent merge is intact by design, and your own
`SessionStart` bind-on-resume finding shows two co-located sessions collide with
no orchestrator/subagent relationship at all.

So candidate 2 stands. Re-measure at your gate to say what changed rather than
assuming either way, and cite `df6f951b` when you do.

## What it means for your branch

Your branch is based on `a69bbac4`. `main` has since moved twice — lane D
(`43c577d4`: a stale-bytecode guard, the `--here` message, default-worktree-layout
coverage) and this merge. Rebase or merge `main` before your own gate, and
**re-measure the baseline at gate time rather than reusing 3057**. The lane-D
commit also means a stale `__pycache__` in your worktree now fails a named test
instead of surfacing as an unrelated assertion — clear it before you measure.

`scripts/hooks/spine_rail.py` and `scripts/run_crew.py` remain fenced from you.
