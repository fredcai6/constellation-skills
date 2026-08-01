# Fence citation — governor-269

This Commander's launch order (`.agent-work/epic-267/crew-handoffs/LAUNCH_ORDER-269.md`, File Ownership
section) states: "The main checkout is **not** fenced: you may read it (you will need to, to compare hook
resolution), but do not write to it."

That is a write-fence on the main checkout's durable `.agent-work/AGENT_FEEDBACK.md` and
`.agent-work/LESSONS.md`. Per `constellation-commander-delegated`'s closeout doctrine ("Fenced
feedback/archive closeout — stage, do not waive"), this run's closeout trio (AGENT_FEEDBACK.md,
lessons-delta.json, CONSTELLATION_FEEDBACK.md) is staged here, worktree-local, under
`.agent-work/staged-feedback/governor-269/`, for the Admiral to harvest into the shared main-checkout root
rather than waiving the feedback/archive gate for fencing.
