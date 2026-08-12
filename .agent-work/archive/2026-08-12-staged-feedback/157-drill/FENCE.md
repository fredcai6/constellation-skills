# Fence citation — 157-drill

This commander run is fenced to its worktree by its Admiral launch order
(`.agent-work/epic-198-burndown/launch-orders/W3-157-drill.md`):

- "Worktree `C:/Programs/cs-wt-drill` … All edits/commits/tests/PR from that worktree only."
- File ownership restricts writes to this commander's own files; the shared durable
  `.agent-work/` root resolves (via git-common-dir) to the MAIN checkout
  `C:\Programs\constellation-skills\.agent-work\`, which this run must not write.

Therefore the feedback/archive durable-log write to the shared root is impossible from
this fenced worktree. Per the delegated-commander fenced-closeout doctrine, the durable trio
is STAGED here worktree-locally instead of waived:

- `AGENT_FEEDBACK.md` — this run's retrospective entry (mentions work id 157-drill)
- `lessons-delta.json` — the applied tick delta (no project-scoped lesson candidates this run)
- `CONSTELLATION_FEEDBACK.md` — two constellation-scoped exports (drill-scenario-decontamination; delegated-commander-in-team-synchronous-crew)

The Admiral harvests this trio into the shared durable `.agent-work/` root before sweeping this
worktree (admiral SKILL closeout §"Harvest before sweep").
