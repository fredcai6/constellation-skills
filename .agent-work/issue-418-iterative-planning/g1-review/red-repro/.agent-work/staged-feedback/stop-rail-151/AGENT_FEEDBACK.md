# Agent Feedback Log (staged — fenced run)

Staged worktree-local copy for work-id stop-rail-151. This run is fenced off the
read-only main checkout per its launch order; the Admiral harvests this entry
into the durable `.agent-work/AGENT_FEEDBACK.md` before sweeping the worktree.

---

## 2026-07-19 — stop-rail-151

**Run shape:** commander (delegated) · init→archive spine, one crew gate g1 (implement/review/integrate) · opus subagents (plan-critic, implementer, reviewer, claude-code-guide fact-check)

**Instruction adherence:** minor deviations
- Followed the spine and gate execution as written. One evidence-driven deviation from the launch order's weak preference: kept plain worktree-comparison (not the deeper per-worktree binding re-key the cold critic argued for) — scoped as the minimal fix for the reported false-positive and routed the clobbering issue to triage. Justified in plan-critic-disposition.md.
- The cold plan critic returned NEEDS-REWORK; rather than accept-or-reject wholesale I triaged its 3 findings (verified one, hardened tests for it, deferred one) — the design-it-twice/critic loop worked as intended.

**Friction / unclear:**
- The spine `understand` step's precondition `p1` ("baseline context loaded") is an *attested* gate but is not auto-satisfied by completing the `context` step — `start understand` refused until I explicitly `attest understand --cond p1`. The chained `start ... >/dev/null` masked the refusal for a beat. Minor: an unmet-precondition refusal could name the attest command in its message.
- Fenced-run feedback/archive closeout doctrine (stage the trio, don't apply to durable LESSONS.md) is spread across the delegated skill prose and the verifier's `_staged_feedback_errors`; having the exact staged file set (AGENT_FEEDBACK.md + lessons-delta.json + CONSTELLATION_FEEDBACK.md + FENCE.md) named in one place in the skill would have saved a read of verify_agent_feedback.py.

**Crew-reported friction:**
- Implementer: the handoff's `_same_path` spec ("normalize via `str(x)`; True on ANY exception") could not literally satisfy Required Evidence (d) — `str(None)`/`str(123)` never raise, so a literal impl returns False for `_same_path(None,"x")` while (d) mandates True. The implementer correctly resolved toward the controlling invariant (non-str → un-comparable → fail-safe True). Handoff-authoring lesson: when a helper's fail-safe path is specified AND its test asserts a specific fail-safe return, make the trigger condition (what counts as "un-comparable") explicit so the spec and the test cannot contradict.
- Reviewer: (1) the survey's `config_ref` (docs/agents/engine-config.json) is a dangling pointer in this source repo — engine degraded gracefully (known, sanctioned). (2) Verifying "binding structure unchanged" required confirming the `worktree` field pre-existed this change (not visible from the diff alone); a one-line handoff note ("the `worktree` field is pre-existing") would have saved the lookup — I had noted the binding *stored* worktree but not that it predated the diff.

**What worked:**
- The cold-plan-critic mechanism earned its keep: it surfaced a load-bearing unverified assumption (Stop payload carries `cwd`) that hand-injected unit fixtures would have masked green. Verifying the harness contract (claude-code-guide → official hooks docs) + making regression test (a) production-shaped (drive the real `handle_post_tool_use` writer path) closed that hole.
- run_crew.py `--backend external` + `--verify-result` gave clean freshness verification of crew artifacts in the Agent-tool harness.

**Improvement signals:**
- When a hook/decision depends on a harness-supplied payload field, verify the field's presence against the harness contract AND make the regression test drive the real writer path — hand-injected fixtures pass green even if the field is absent in production. → disposition: distilled to a lesson (banked, project scope, bank_reason in lessons-delta.json — needs one re-observation to confirm it is a repeated pattern worth a testing-conventions doc, alongside test-harness-concurrency-failsafe).
- Handoff-authoring: keep a fail-safe helper's spec and its asserted test return internally consistent. → disposition: none (one-off handoff wording, fixed in the moment by the implementer; not worth banking).
