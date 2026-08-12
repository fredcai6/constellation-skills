# Agent Feedback Log

Unified, append-only retrospective across Constellation runs in this repo. Each Commander run appends one entry at the `feedback` step, just before archive/commit. Purpose: capture where the workflow, skills, templates, or context made the work harder than it needed to be, so the doctrine improves over time.

This is workflow-improvement signal, not project truth. It accumulates across work-ids and is **never** archived or moved with a single run — it lives at the root of the agent work area and persists. Recurring entries are evidence for a Charter refresh or a template change. Distill a concrete interface/field/doctrine fix into a lesson carrying a `target`, settled at the Commander `feedback` step's forced apply-or-defer gate; use this log for the broader "how did the run actually go" retrospective.

Be honest. An entry that only says "went fine" teaches nothing.

Newest entries on top.

---

## `2026-07-19` — `cg-fastfollows-198`

**Run shape:** `commander (delegated)` · spine init→archive (10 steps) + execute.json (2 crew gates × implement/review/integrate) · subagent tiers: opus (4 crews: 2 implementer, 2 reviewer)

**Instruction adherence:** `fully followed`
- Drove the full spine through the engine (installed workbench copy) while the tests exercised the repo's `scripts/checklist_engine.py` under edit — deliberate isolation for this meta-run (editing the very engine that would otherwise drive the spine). Auto-detected `--skill-dir` resolved spine postconditions to the stable installed scripts, which made that isolation free.
- Delegated `user-decision` checkpoints satisfied by citing launch-order sections; filing new issues correctly treated as outside inherited latitude → all 3 triage candidates deferred to the Admiral, none filed.

**Friction / unclear:**
- The plan/survey templates' `config_ref: docs/agents/engine-config.json` points at a path that does not exist in a skill-source repo. The engine degrades gracefully, but **all four crews** independently rediscovered the house convention (inline `config`) — a recurring, avoidable lookup. Banked as lesson `config-ref-absent-skill-source`.
- The spine's `understand`/`plan`/`execute` steps each needed a precondition attest (`p1`) before `start` — obvious in hindsight, but the RAIL output on the refused `start` was truncated by my own `grep -v RAIL | head`, briefly hiding the "preconditions unmet" reason. Self-inflicted; noting so a future run keeps the refusal line visible.

**Crew-reported friction:**
- g1-implementer: the #189 test sub-bullet asked to "assert the `why_ref` pointer" on the survey `REFRESH REQUESTED:` line, which is **unrealizable under the minimal fix** (a survey has no why_trail → `_latest_why_record` is None → no `(why_ref …)` suffix). The implementer correctly did the minimal fix and asserted line+seam+DIGEST-absent. Handoff test-spec overreach; banked as `handoff-test-assertion-realizable-per-type`.
- g2-implementer + g2-reviewer: doc handoff cited absolute line numbers ("L205 area") that shift as edits land; **prefer section/symbol anchors** in doc handoffs. Banked as `doc-handoff-anchor-not-line-number`.
- g2-reviewer: the reviewer had to rediscover the engine CLI shape (`--file` is a top-level arg before the subcommand; `current` takes no `--session-id`) via a usage error — a one-line quick-start in the reviewer handoff/skill would save a round-trip.
- g1-reviewer: driving the review survey with the **independent installed** engine (not the under-review worktree copy) was the right call and worth stating explicitly in reviewer handoffs for engine-change reviews.

**What worked:**
- The fully-specified, per-fix handoffs (line anchors + exact expected behavior + backward-compat constraint + "prove the new tests fail pre-fix") produced correct implementations first try and rigorous reviews — the g1 reviewer reconstructed the pre-fix engine in scratch and proved the #190/#191 tests fail against it. No rework rounds, no BLOCK verdicts, zero reopens across both gates.
- The `#179` fail-closed `--why`/`--mechanical` gate dogfooded cleanly at every advance — including on the crews' own implementer plans — which is exactly the behavior this PR documents.

**Improvement signals:**
- `config_ref` template path is skill-source-hostile → disposition: distilled to lesson `config-ref-absent-skill-source` (needs-human apply; a template change is doctrine, deferred to Admiral/Charter in this autonomous run).
- Doc handoffs should anchor on symbols/sections, not line numbers → disposition: distilled to lesson `doc-handoff-anchor-not-line-number`.
- Handoff test-assertion specs should be realizable for the type under test → disposition: distilled to lesson `handoff-test-assertion-realizable-per-type`.

---
