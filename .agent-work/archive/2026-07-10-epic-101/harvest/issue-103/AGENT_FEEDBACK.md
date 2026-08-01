# Agent Feedback Log

Unified, append-only retrospective across Constellation runs in this repo. Each Commander run appends one entry at the `feedback` step, just before archive/commit. Purpose: capture where the workflow, skills, templates, or context made the work harder than it needed to be, so the doctrine improves over time.

This is workflow-improvement signal, not project truth. It accumulates across work-ids and is **never** archived or moved with a single run — it lives at the root of the agent work area and persists. Recurring entries are evidence for a Charter refresh or a template change. Distill a concrete interface/field/doctrine fix into a lesson carrying a `target`, settled at the Commander `feedback` step's forced apply-or-defer gate; use this log for the broader "how did the run actually go" retrospective.

Be honest. An entry that only says "went fine" teaches nothing.

Newest entries on top.

---

## 2026-07-10 — issue-103

**Run shape:** commander · full 10-step spine + 4 crew gates (g1-g4, each implement/review/integrate) · crews at inherited tier (general-purpose subagents, external backend)

**Instruction adherence:** fully followed
- Drove the full spine through the repo's own vendored engine (`scripts/checklist_engine.py`) and templates (`skills/commander/templates/`), per the dogfooding lesson. Delegated mode throughout: satisfied the four `user-decision` checkpoints by citing LAUNCH_ORDER sections (no reachable human). Crew gates dispatched via `run_crew.py --dispatch external` + `--verify-result` (no headless CLI in this harness), implementer/reviewer as synchronous Agent-tool subagents.
- Ran plan-alternatives (2 decomposition candidates → convergence) and a cold plan critic (bias-to-yes); folded all 6 critic should-fix findings into the gate handoffs before execution.

**Friction / unclear:**
- Dogfooding split: the spine template's `<commander-skill-dir>/scripts/...` placeholder assumes an installed layout (scripts under the skill dir). This source repo vendors scripts at repo root `scripts/` and templates under `skills/commander/templates/`. Resolved by instantiating with `--skill-dir <repo-root>` so engine-checked `command` postconditions resolve to `./scripts/`, and driving template paths from `skills/commander/` by judgment. A one-line note in the dogfooding lesson would save the lookup.
- `checklist_engine.py record` requires `--result`; a bare `record --note` errors. Minor; used `attest` + report instead.
- The EXECUTE_PLAN template is TDD-shaped (implement/review/integrate with a test command). For an inspection-only doc diet it fits, but the `gN-integrate` `command` postcondition wants a "tests pass" command — I pointed it at the structural suite, which is the honest proxy here (the real evidence is the reviewer's grep + meaning-preservation check).

**Crew-reported friction:**
- Every crew praised the same pattern: exact BEFORE/AFTER blocks + an explicit MUST-SURVIVE operative-fact list + a forbidden-signature list made register-sensitive diet gates deterministic and independently verifiable. One implementer flagged that "before (439 words)" vs a "body" draft could invite a body-only mis-comparison — name which count is meant.
- One implementer noted the plan `config_ref docs/agents/engine-config.json` is absent in this repo (tolerated as defaults); a handoff note would pre-empt the lookup.

**What worked:**
- Cold plan critic earned its keep: finding #6 (pointer-name / forbidden-signature preservation is NOT covered by the structural suite — suite-green is a false assurance) directly shaped the per-gate reviewer greps and caught a real gap between the constraint and its evidence surface.
- `run_crew.py` external backend + `--verify-result` gave clean freshness verification of each crew result without a headless CLI.

**Improvement signals:**
- For a doc-diet/register run, make pointer-name + forbidden-signature preservation an explicit per-gate reviewer grep — do not trust a structural suite to guard prose. → disposition: distilled to a lesson with a target (deferred at feedback; not ripe on first observation).
- The register-sensitive-diet handoff recipe (exact before/after + MUST-SURVIVE facts + forbidden signatures) should be the standard shape for meaning-preserving doc edits. → disposition: distilled to a lesson (deferred; not ripe).
- Dogfooding `--skill-dir` resolution detail (above). → disposition: distilled to a lesson (deferred; not ripe).
