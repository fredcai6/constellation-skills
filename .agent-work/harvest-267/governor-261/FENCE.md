# Fence citation — governor-261

This Commander is dispatched under `.agent-work/epic-267/crew-handoffs/LAUNCH_ORDER-261.md`
(Admiral epic #267), whose "Data Locations" section fences the main checkout's `.agent-work/` as
read-only for this run: "Read these; do not write to any of them. Your writes stay inside your
worktree." That fence extends to the durable `.agent-work/AGENT_FEEDBACK.md` and
`.agent-work/LESSONS.md`, both of which live in the main checkout, not this worktree
(`C:/Programs/constellation-skills-wt/governor-261`).

Per this run's own commander-delegated skill doctrine ("Fenced feedback/archive closeout — stage,
do not waive"): the feedback-step durable-log write is impossible under this fence, so this
directory stages the trio in lieu of the durable-root write — `AGENT_FEEDBACK.md` (the entry that
belongs in the shared log), `lessons-delta.json` (unapplied — the Admiral applies it against the
real shared `LESSONS.md` at epic harvest, since applying it here would either fail against this
worktree's absent playbook copy or fork a duplicate playbook), and `CONSTELLATION_FEEDBACK.md`
(nothing ripe to export this run, stated explicitly). This `FENCE.md` is the required citation
`verify_agent_feedback.py` looks for to accept the staged trio in lieu of the durable-root write.
