# Roadmap notes

Forward-looking threads deliberately not yet cut into issues. Each entry names its origin so the context is recoverable when it's picked up.

## Execution-discipline imports (from the superpowers comparison)

Origin: 2026-07-09 research synthesis behind #99 (design-it-twice generalization). The design phase is now constellation's strength — parallel alternatives + cold critic panels, both mechanized. The comparison found superpowers' remaining edge is the **execution** phase; candidates to evaluate for import, each against its existing constellation equivalent (deletion-test before adopting):

- **Durable progress ledger** that survives compaction/session death (their `.superpowers/sdd/progress.md`) vs our STATE_NOTE + crew registry — theirs records per-task outcomes, ours records process state.
- **File-based handoff hygiene** for controller-context economy (task-brief/report/review-package scripts keeping the orchestrator context clean).
- **Explicit model-tier selection per role** (cheap implementers, strongest model for the final broad review) — we say "pick tier from complexity" but don't mechanize it.
- **Pre-flight plan-conflict scan** before executing a frozen plan.

Related unshipped-elsewhere idea already landed here instead: competitive-critic mode (opt-in) in the critical-review standard.
