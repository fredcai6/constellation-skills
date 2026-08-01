# Agent Feedback Log (staged — 152-engine-verbs)

Staged for Admiral harvest into the durable `.agent-work/AGENT_FEEDBACK.md` (this run is fenced off the main checkout per the launch order). Newest on top.

---

## `2026-07-19` — `152-engine-verbs`

**Run shape:** `commander (delegated)` · spine init→archive, execute.json e0+g1(impl/review/integrate)+g2 · subagent tiers: opus (plan critic, implementer, reviewer)

**Instruction adherence:** `fully followed`
- Drove the whole spine through the engine (no hand-edited JSON); crews dispatched as synchronous Agent-tool subagents (external backend, no CLI harness here) per crew-dispatch.md.
- Reconciled the launch order's assumed baseline against the actual code before planning — this caught that sub-fix 3 was already shipped (#32), exactly the "headline mechanism may already be shipped" warning in commander-core.

**Friction / unclear:**
- The launch order framed three sub-fixes as to-build, but one (heartbeat-on-mutate) was already fully implemented in #32. The Honest-Null Clause covered it, but a delegated commander must actively verify each sub-fix against the code rather than trust the order's framing — worth making a standing pre-plan check, not a per-run rediscovery.
- Spine `reconcile` had no packet map and its structural doc (CHECKLIST_SCHEMA.md) was fenced, so the only compliant move was a reasoned deferral. The doctrine covers this ("record a reasoned no-op as compliant"), but the fenced-doc case (record exists, but I can't touch it) is a slightly different shape than the no-map case.

**Crew-reported friction:**
- Implementer: the frozen handoff omitted two negatives it had to rediscover — that `resume` must NOT be added to `RAIL_VERBS` (a frozen exact-set assertion), and the test mode (test-after). A one-line "do not touch RAIL_VERBS; test-after" in the handoff would have saved a lookup.
- Reviewer: the "resume cannot un-escalate a rework-cap block" guarantee actually lives in `reopen`'s escalation branch (no prior_status recorded), not in `resume` itself — a handoff pointer to where an invariant is anchored (not just asserted) speeds an adversarial review.
- Both crews: the plan-template `config_ref: docs/agents/engine-config.json` points at a file absent in this repo; each crew degraded to an inline config. Harmless but re-encountered per crew.

**What worked:**
- The cold plan critic (opus, no authoring context) earned its keep: it found three real state-transition defects (retext-check smuggling satisfaction past waived/attested short-circuits; shallow-copy aliasing breaking all-or-nothing; resume un-escalating a cap block) BEFORE any code was written, so the implementer applied an already-hardened design and the reviewer reproduced each invariant green.
- Reasoning-gate for the honest-null sub-fix kept the measured negative first-class in the spine instead of a side note.

**Improvement signals:**
- Add a standing delegated-commander pre-plan step: "verify each launch-order sub-fix against the actual code (grep the named symbol) before planning; a sub-fix already shipped becomes an honest-null, not a build gate." → disposition: distilled to a lesson (mention; thin — one observation, re-observe before banking).
- Handoff template could prompt for "invariants this change relies on that live in OTHER functions" so the reviewer knows where to look. → disposition: route to a Charter/template-refresh candidate (needs human).
