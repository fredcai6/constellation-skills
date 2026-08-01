# Fence citation — issue #303

Staged here instead of the durable main-checkout `.agent-work/AGENT_FEEDBACK.md` /
`LESSONS.md` because this run operates under a frozen Admiral launch order that
fences the durable root off:

> `.agent-work/` at the main checkout is **read-only to you** while the Admiral's
> epic lease is active. Your own `.agent-work/` resolves to your **worktree**
> root; that is expected under an epic, not a bug.
>
> — `C:/Programs/constellation-skills/.agent-work/epic-298/launch-orders/LAUNCH_ORDER-303.md`, "Data Locations"

The launch order's own Return Shape section additionally directs staging this
exact trio here:

> Also stage your durable trio worktree-locally at
> `.agent-work/staged-feedback/303/` (lessons-delta, `AGENT_FEEDBACK.md` entry,
> `CONSTELLATION_FEEDBACK.md` exports) so the Admiral can harvest it before the
> worktree is swept.
>
> — same launch order, "Return Shape"

The Admiral harvests this trio into the shared durable `.agent-work/` at the
main checkout before this worktree is swept (`git worktree remove`).
