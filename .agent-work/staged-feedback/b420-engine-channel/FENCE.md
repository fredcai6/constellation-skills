# Fence citation — b420-engine-channel

`scripts/agent_work_root.py durable_root()` run from this worktree resolved to the worktree itself,
not the main checkout — it detected an ACTIVE Admiral epic lease
(`claimed_by == "admiral"`, `status == "active"`) on `C:/Programs/constellation-skills/.agent-work/
epic-418/spine.json`, consistent with the Admiral actively driving epic #418 during this run (it
messaged me mid-task). Per `agent_work_root.py`'s own documented exception: "the main checkout is
fenced read-only (per the launch order), so redirecting durability there would point the
feedback/archive gate at an unwritable path."

Citing: launch order `.agent-work/epic-418/launch-orders/B-420.md` + `_COMMON.md`'s Data Locations
section (`.agent-work/`, including `LESSONS.md`/`AGENT_FEEDBACK.md`, lives in the main checkout;
I am dispatched into an isolated worktree with no write mandate over the main checkout outside the
pre-cleared `git push` on `epic-418/*` and `gh` operations named there).

Staging the AGENT_FEEDBACK.md entry, lessons-delta.json, and CONSTELLATION_FEEDBACK.md exports here
per `constellation-commander-delegated`'s "Fenced feedback/archive closeout — stage, do not waive"
clause. The Admiral harvests this trio into the shared root before sweeping this worktree.
