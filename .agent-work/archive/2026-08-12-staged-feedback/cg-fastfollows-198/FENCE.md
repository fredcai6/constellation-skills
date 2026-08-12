# Fence citation — cg-fastfollows-198

This delegated Commander run is fenced off the shared main-checkout durable
`.agent-work/` root by its Admiral launch order.

- **Launch order:** `.agent-work/epic-198-burndown/launch-orders/W1-A-cg-fastfollows.md`
- **Fence source:** Launch order §"Data Locations" designates the main checkout
  (`C:/Programs/constellation-skills`) as read-only reference material — "do not write".
  The durable feedback root (`durable_root()`) resolves to that main checkout, which
  this run must not write. §"File Ownership" scopes this run's writes to
  `scripts/checklist_engine.py`, `docs/CHECKLIST_SCHEMA.md`, and engine tests only.
- **Worktree:** `C:/Programs/cs-wt-cg` (branch `fix/cg-fastfollows-198`).

Per the constellation-commander-delegated "Fenced feedback/archive closeout" rule, the
feedback/archive durable-log write is staged here as the worktree-local trio
(`AGENT_FEEDBACK.md`, `lessons-delta.json`, `CONSTELLATION_FEEDBACK.md`) plus this
citation, in lieu of the durable-root write. The Admiral harvests this trio into the
shared durable root before sweeping the worktree.
