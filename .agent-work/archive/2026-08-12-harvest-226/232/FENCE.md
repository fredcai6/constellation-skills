# Fence citation — work-id 232

The main checkout (`C:/Programs/constellation-skills`) carries an ACTIVE
Admiral epic-226 lease at `.agent-work/epic-226/spine.json`
(`engine_session.status == "active"`, `claimed_by == "admiral"`,
`session_id: admiral-epic-226-b`, confirmed by direct read at this run's
`context` step, 2026-07-25). Per `agent_work_root.py`'s documented fencing
exception, an active Admiral epic lease fences the main checkout's durable
`.agent-work/` read-only for a delegated Commander, so `durable_root()`
resolves to this worktree instead of the shared main-checkout root.

Per `constellation-commander-delegated`'s fenced-feedback-closeout
guidance and `LAUNCH_ORDER-232.md`'s own File Ownership section (the
Commander's two carve-outs into the main checkout are the findings file
and the verdict file — NOT the shared `AGENT_FEEDBACK.md`/`LESSONS.md`
trio), this run stages its feedback trio here
(`.agent-work/staged-feedback/232/`) rather than writing the shared
durable log directly. The Admiral harvests this trio into the shared root
at epic closeout, then sweeps this worktree.

Staged trio: `AGENT_FEEDBACK.md` (this run's retrospective entry),
`lessons-delta.json` (tick + confirm ops against the 4 active lessons
this run exercised — NOT applied against the live `.agent-work/LESSONS.md`
under the fence; the Admiral applies it), `CONSTELLATION_FEEDBACK.md`
(no constellation-scoped lesson ripe for export this run — stated with
reason, not a bare none).

Cited launch order: `.agent-work/epic-226/launch-orders/LAUNCH_ORDER-232.md`.
