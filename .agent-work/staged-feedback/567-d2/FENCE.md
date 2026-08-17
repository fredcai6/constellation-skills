# Fence note — 567-d2

The durable-root `CONSTELLATION_FEEDBACK.md` export normally lives outside this worktree, in
the main checkout, which this run's launch order fences as read-only:

> The main checkout is `/home/tommy/projects/constellation-skills` — readable if you need it,
> **never** writable by you.
> — LAUNCH_ORDER.md, "Data Locations"

Per `constellation-commander-delegated`'s delegated-specific closeout doctrine ("Fenced
feedback/archive closeout"): episodes are written normally (`episodes/` is tracked inside this
worktree, unaffected by the fence), but the `CONSTELLATION_FEEDBACK.md` export is staged here —
`.agent-work/staged-feedback/567-d2/CONSTELLATION_FEEDBACK.md` — for the Admiral to harvest into
the durable root before sweeping this worktree, rather than waived.
