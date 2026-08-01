# Agent Feedback Log

Unified, append-only retrospective across Constellation runs in this repo. Each Commander run appends one entry at the `feedback` step, just before archive/commit. Purpose: capture where the workflow, skills, templates, or context made the work harder than it needed to be, so the doctrine improves over time.

This is workflow-improvement signal, not project truth. It accumulates across work-ids and is **never** archived or moved with a single run — it lives at the root of the agent work area and persists. Recurring entries are evidence for a Charter refresh or a template change. Distill a concrete interface/field/doctrine fix into a lesson carrying a `target`, settled at the Commander `feedback` step's forced apply-or-defer gate; use this log for the broader "how did the run actually go" retrospective.

Be honest. An entry that only says "went fine" teaches nothing. The useful entries name the exact step, field, or instruction that was ambiguous, missing, contradictory, or routinely improvised around. A `none` bullet requires a run-specific reason (`none — confirmed after review: <what you checked>`); entries whose signal sections are all bare `none` fail the feedback invariant check.

Newest entries on top.

---

## `2026-07-19` — `118-durable-root`

**Run shape:** `commander (delegated)` · `spine init→archive; execute.json g1 (crew) + g2 (crew)` · `opus implementer/reviewer crews; opus explore for grounding`

**Instruction adherence:** `fully followed`
- Followed the delegated-commander spine end to end through the engine; both gates dispatched fresh-context implementer + independent reviewer crews via `run_crew.py --backend external` + `--verify-result` (the sanctioned Agent-tool path — no headless `claude` CLI in this harness).
- One judged deviation: folded g1's reviewer-surfaced non-blocking robustness nit (the `glob()` OSError could escape mid-iteration) in myself at integrate as a strictly-defensive one-line `list()` hardening and re-ran the full suite, rather than a rework round-trip for one line on a "never raises" contract. Recorded in the g1-integrate why and the report.

**Friction / unclear:**
- The engine requires a step's null **preconditions** to be attested *before* `start`; several `start` calls were REFUSED until I attested p1 first, then re-ran `start`. The `current` imperative narrates postconditions but not this precondition-attest-before-start ordering — a one-line hint ("attest preconditions, then start") would have saved three retry round-trips at understand/plan/g1-review/g1-integrate.
- The `gN-integrate` c2 (`review-result` verdict match) is checked against evidence attached to the **integrate** task, not the `gN-review` task where the reviewer verdict was first recorded; I had to re-`attach` the same review-result onto integrate. Not obvious from the template.

**Crew-reported friction:**
- Both implementer crews noted the repo has no `docs/agents/engine-config.json` (the spine `config_ref`), so the engine degrades to defaults — benign and already doctrine, but every crew re-flags it. A one-line "config_ref absent-by-design in this repo" in the crew handoff preamble would stop the re-flag.
- g2 implementer: an IMPLEMENTER_HANDOFF anchor phrased as "after the line ending …X" was ambiguous when a second related sentence followed in the same section; pinning the exact following line removes it (handoff-authoring nuance, understood — not banked).
- g2 reviewer: the reviewer skill frames a docs-only Fowler pass as a "skip" needing an independent co-sign, but a genuine all-`absent` per-smell verdict is a *completed* pass; the framing invites a false `rail_exception`. Banked as a lesson to re-observe (target: reviewer skill).

**What worked:**
- Pre-authoring the doc-only invariant chain as a runnable check (`check_doc_invariants.py`) made g2's doc-edit gate mechanically verifiable — it was red pre-edit and green post-edit, and the reviewer reproduced it. This is the doc-only-gate doctrine paying off exactly as intended.
- The Explore-agent grounding pass before authoring the g2 handoff (surfacing that "residual-guard signature list" = the `retired` tuple in `test_install_constellation.py`) let me pre-author near-verbatim content, so the implementer applied it deterministically with zero paraphrase-drift (reviewer: word-diff additions-only, 0 findings).

**Improvement signals:**
- Engine `current` output should hint "attest null preconditions before `start`" (or `start` should auto-surface unmet preconditions to attest). → disposition: `distilled to a lesson (deferred needs-human — engine/doctrine target)`
- Reviewer skill: add an explicit "docs-only Fowler pass" clause so a genuine all-absent verdict is a completed pass, not a skip needing co-sign. → disposition: `distilled to a lesson with target=reviewer skill (deferred needs-human — doctrine)`
- **Dogfood confirmation (not friction):** this very entry passed the `feedback` c1 gate worktree-local — `durable_root()` resolved to the worktree under the active epic-198 admiral lease (the exact item-4 mechanism this run shipped), so no staging dance and no force-waive was needed. The fix demonstrably fixes its own gate. → disposition: `none — confirmed by the passing c1 check under the live epic lease`
