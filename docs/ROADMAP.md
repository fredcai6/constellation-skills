# Roadmap notes

Forward-looking threads deliberately not yet cut into issues. Each entry names its origin so the context is recoverable when it's picked up.

## Execution-discipline hardening

Origin: 2026-07-09 research synthesis behind #99 (design-it-twice generalization). The design phase is now constellation's strength — parallel alternatives + cold critic panels, both mechanized. What's left is sharpening the **execution** phase; each candidate below is evaluated against the deletion test (if we removed this, would something concrete break?) before it gets cut into an issue:

- **Durable progress ledger** that survives compaction/session death, layered onto our STATE_NOTE + crew registry, which today records process state rather than per-task outcomes.
- **File-based handoff hygiene** for controller-context economy (task-brief/report/review-package scripts keeping the orchestrator context clean).
- **Explicit model-tier selection per role** (cheap implementers, strongest model for the final broad review) — we say "pick tier from complexity" but don't mechanize it.
- **Pre-flight plan-conflict scan** before executing a frozen plan.

Related unshipped-elsewhere idea already landed here instead: competitive-critic mode (opt-in) in the critical-review standard.

## Permanent base rigor rules + simplified charter setup

Origin: 2026-07-09 epic-101 hygiene pass (#105). The author is the real user of these rules, not a hypothetical broader audience; rigor is worth the cost it imposes, so the default should assume it rather than make it opt-in.

- Fold the currently scattered rigor expectations into a small set of permanent base rules rather than per-project configuration.
- Simplify constellation-charter's setup path to fewer knobs — reduce the number of choices a fresh repo has to make before it can adopt the doctrine.

## Canonize issues/specs ↔ architecture interplay

Origin: 2026-07-09 epic-101 hygiene pass (#105). Deliberately deferred: the human has strong feelings about how issue/spec authoring and the architecture map (`docs/architecture/`) should check each other, and wants to weigh in directly before this is designed rather than have an agent propose a shape first.

- Decide which of issues/specs and the architecture map leads and which follows as both evolve, and where each one is allowed to override the other.

## Interrogator finish-gate

Origin: 2026-07-09 epic-101 hygiene pass (#105).

- Add an explicit human sign-off step confirming constellation-interrogator's questioning is actually complete, not just that the loop terminated.
- Fold this gate into the Pocock 1.1-release evaluation rather than shipping it as a standalone mechanism.

## Aggressive playbook clearing, feedback maintenance to the curator

Origin: 2026-07-10 epic-101 closeout (human direction at acceptance). The playbook sits at its 20-active cap and the epic's lessons audit had to route good candidates off-playbook; meanwhile dormancy ticks are the only clearing mechanism and they cull by clock, not by judgment.

- Clear the playbook more aggressively: raise the bar for staying active (recurrence or a named consumer), and make retire-on-audit the norm rather than waiting out dormancy.
- Move standing feedback maintenance (AGENT_FEEDBACK / CONSTELLATION_FEEDBACK grooming, playbook pruning proposals) into the curator's periodic run — it already owns measure-then-mend for the corpus; the learning logs are corpus too.
- Ties into the queued dormancy-mechanism note (tick-burst culling) and the epic-101 audit's withheld tick.

## Plain-language register — rein in the project sub-dialect

Origin: 2026-07-10 epic-101 closeout (human direction). Sessions have grown jargony: a technical human reports the project-specific sub-dialect (spines, gates, waves, harvests, durable trios, honest nulls...) is blowing past them. The vocabulary is load-bearing for agents but must not price the human out of their own project.

- Human-facing surfaces (checkpoint summaries, reports, epic summaries, interrogator/commander human entries) should default to plain language, with the term of art in parentheses on first use at most.
- Consider a small glossary the docent/curator maintains, and a register rule: project dialect is for agent-to-agent artifacts; human-facing text explains itself.
- Curator lint candidate: flag doc surfaces tagged human-facing whose density of coined terms exceeds a heuristic.

## Cross-harness compatibility: Codex as well as Claude

Origin: 2026-07-10 epic-101 closeout (human direction). Skills today assume the Claude Code harness (Skill tool, Agent-tool subagents, `claude -p` headless, permission classifier behaviors). Constellation should be loadable from Codex-family agents too.

- Audit hard Claude-isms: harness-specific tool names in doctrine, `claude` CLI invocations in scripts (run_crew backends, run_skill_eval launch seam), permission-model assumptions.
- The eval runner's injectable launch seam is the right shape — extend the backend pattern (cli/external) to a codex backend where dispatch is needed.
- Keep SKILL.md bodies harness-neutral; isolate harness bindings in per-harness reference files (precedent: `_shared/windows.md` for platform quirks).
