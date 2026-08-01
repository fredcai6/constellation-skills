# Agent Feedback Log

Unified, append-only retrospective across Constellation runs in this repo. Workflow-improvement signal, not project truth. Newest entries on top.

---

## 2026-07-10 — issue-104 (constellation-curator, epic-101 cluster C)

**Run shape:** commander (delegated) · full spine, 5 execute gates (4 crew gates + 1 reasoning acceptance gate) closed · crew tiers: opus for the two new-module builds (G1 script, G2 skill) + G3 tests, sonnet for G4 wiring and all reviewers + the independent acceptance sweep.

**Instruction adherence:** fully followed.
- Drove the whole spine and execute plan through the repo's OWN engine/templates/scripts (dogfooding), not installed copies. init_work_area, checklist_engine, run_crew (external backend), verify_state_note, verify_agent_feedback all exercised from `scripts/`.
- Delegated checkpoints (understand/plan/triage/review) satisfied by attaching `user-decision` artifacts citing the frozen launch order, as the commander-core delegated mode specifies.
- One self-caught process slip (see Friction): dispatched the g2 reviewer before closing g2-implement in the engine; the engine refused the out-of-order advance ("not the active gate") and I closed g2-implement first. The guardrail worked.

**Friction / unclear:**
- `init_work_area.py --spine` refused an explicit `--skill-dir skills/commander` because that dir carries no `scripts/` in the source repo (issue-99 T2 refusal, working as intended). Omitting `--skill-dir` (auto-detect) resolved `<commander-skill-dir>` to the repo root and materialized a runnable spine. The refusal message already tells you to omit it — no doc gap, just noting the source-repo path.
- The spine template resolves `<commander-session-id>` to `commander-issue-104`; I initially claimed the lease as `commander-104` and had to release + reclaim. Minor: claim the lease AFTER reading the materialized spine's resolved session-id, not before.
- Closing a crew gate is three engine calls in strict order (attest p1 → start → attach result → advance), and the review/integrate gates cannot advance until the implement gate is closed. Easy to batch wrong. A one-line "close-gate recipe" note near the gate-execution doctrine would help.

**Crew-reported friction:**
- G1/G3 seam (harvested): the finding `status` vocabulary (`flagged`/`shortlist`/`info`/`ok`) was implied in prose but never enumerated as a closed set in the G1 handoff; G3 had to reverse-engineer the exact strings to assert on them. A tiny shared contract fragment naming the vocabulary would remove the guess. (I mitigated by telling the G3 implementer to read the strings from `curate_corpus.py` source.)
- G2 (harvested): the curator SKILL.md had to cover 8 body topics AND pass curate_corpus's own 400-word size budget (dogfood) — two requirements that pull against each other; the handoff didn't flag the tension, costing several trim passes. A handoff line "these topics must fit the word budget; write tight" would set the expectation.
- G3/G4 (harvested): the IMPLEMENTER_PLAN template models a TDD red/green flow that doesn't fit a test-after/evidence-only gate; crews collapsed to the template's own single-postcondition fallback each time. The template covers it, but a crew hand-set `status: done` once and wedged the engine (only `complete` transitions cleanly) — a template comment "never hand-set status; let the engine transition it" would prevent it.

**What worked:**
- The two-sided acceptance (T5) worked exactly as designed. The mechanical detector (curate_corpus.py) and the independent fresh-context sweep — given neither the script nor the fix list — CONVERGED on the same duplication finding set. The only differences were the pointer-vs-doctrine SEMANTIC judgments the script deliberately does not make (T7); that split is precisely why the independent judgment ADDED value instead of echoing the script. Strong evidence the detector isn't self-confirming.
- The cold plan critic earned its keep: it caught a real BLOCKER (a hardcoded `SKILL_NAMES` full-set assertion that would have red-ed the suite at the G2 boundary, silently falsifying "green at every gate"). Folding the one-line fixture fix into G2 kept the boundary green. Bias-to-yes on the single-critic-vs-panel choice was right for a bounded single-issue plan.
- `run_crew.py --dispatch external` + synchronous Agent-tool subagents + `--verify-result` was a clean, durable crew loop with no CLI backend. Reviewers reproduced every claim independently (one even performed a real non-tautology spot-check by flipping an expected status and confirming red, then reverting).

**Improvement signals:**
- Enumerate the curate_corpus finding `status`/`check` vocabulary in a small shared contract both the tool and its tests read. → disposition: distilled to a constellation lesson (exported for epic harvest; target = a curator/curate_corpus contract fragment).
- Handoffs that impose a dogfood/self-check budget on an authored artifact should name the budget-vs-content tension explicitly. → disposition: distilled to a constellation lesson (exported).
- In-process teammates cannot spawn background subagents in this harness; all crew dispatch is synchronous. → disposition: mention (contradicts the general "prefer background subagent dispatches" preference — scope that preference to non-teammate contexts).
