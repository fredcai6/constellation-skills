# Fence citation — issue #228

This Commander ran under a frozen Admiral launch order:
`C:/Programs/constellation-skills/.agent-work/epic-226/launch-orders/LAUNCH_ORDER-228.md`

Its **Data Locations** section marks the main checkout's `.agent-work/` tree
(the whole tree — lessons inbox, prior epic archives, the Admiral's live
spine) **read-only for this Commander**, carving out only two explicit write
exceptions: the verdict at `.agent-work/epic-226/verdicts/commander-228.md`
and the findings file at `.agent-work/epic-226/evidence/findings-228.md`. The
durable feedback/lessons logs (`AGENT_FEEDBACK.md`, `LESSONS.md`,
`CONSTELLATION_FEEDBACK.md`) are not among those carve-outs, so this
Commander cannot append to them directly.

Per `constellation-commander-delegated`'s fenced feedback/archive closeout
guidance, the feedback-step trio is staged here instead
(`AGENT_FEEDBACK.md`, `lessons-delta.json`, `CONSTELLATION_FEEDBACK.md`) for
the Admiral to harvest into the shared durable root at
`C:/Programs/constellation-skills/.agent-work/`.
