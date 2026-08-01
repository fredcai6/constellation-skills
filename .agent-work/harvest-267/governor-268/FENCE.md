# Fence citation — governor-268

This Commander is dispatched under `.agent-work/epic-267/crew-handoffs/LAUNCH_ORDER-268.md`
(Admiral epic #267), whose "Workspace" and "File Ownership" sections fence the main checkout's
`.agent-work/` as read-only for this run ("The main checkout is not fenced for reading; do not
write to it") and direct: "Stage your closeout trio at `.agent-work/staged-feedback/governor-268/`
on your PR branch for the Admiral's harvest."

Per this run's own commander-delegated skill doctrine ("Fenced feedback/archive closeout — stage,
do not waive"): the feedback-step durable-log write is impossible under this fence, so this
directory stages the trio in lieu of the durable-root write — `AGENT_FEEDBACK.md` (the entry that
belongs in the shared log), `lessons-delta.json` (unapplied — the Admiral applies it against the
real shared `LESSONS.md` at epic harvest), and `CONSTELLATION_FEEDBACK.md` (nothing ripe to export
this run, stated explicitly). This `FENCE.md` is the required citation `verify_agent_feedback.py`
looks for to accept the staged trio in lieu of the durable-root write.
