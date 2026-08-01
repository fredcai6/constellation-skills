# Fence citation — corpus-id-153

This run is a delegated Commander dispatch under the Admiral launch order at
`.agent-work/epic-198-burndown/launch-orders/W1-B-corpus-id.md` (issue #153, wave-1 dispatch B).

**Why the durable feedback log was staged, not written directly:** the launch order (Workspace section)
fences all work to the worktree `C:/Programs/cs-wt-corpus` and states edits/commits/tests/PR happen from
the worktree, "never the shared checkout." The durable `AGENT_FEEDBACK.md` resolves to the shared main
checkout (`C:/Programs/constellation-skills/.agent-work/AGENT_FEEDBACK.md`), which is concurrently
writable by the other active wave-1 commander (commander-cg). Appending to that shared log from parallel
delegated commanders risks a clobber, so per the `constellation-commander-delegated` doctrine
("Fenced feedback/archive closeout — stage, do not waive") this run stages the complete trio
(AGENT_FEEDBACK.md entry, lessons-delta.json, CONSTELLATION_FEEDBACK.md export) here under
`.agent-work/staged-feedback/corpus-id-153/` for the Admiral to harvest into the shared root before
sweeping this worktree.
