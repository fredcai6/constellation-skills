# Agent Feedback Log

Unified, append-only retrospective across Constellation runs in this repo. Each Commander run appends one entry at the `feedback` step, just before archive/commit. Purpose: capture where the workflow, skills, templates, or context made the work harder than it needed to be, so the doctrine improves over time.

This is workflow-improvement signal, not project truth. It accumulates across work-ids and is **never** archived or moved with a single run — it lives at the root of the agent work area and persists.

Newest entries on top.

---

## `2026-07-19` — `corpus-id-153`

**Run shape:** commander (delegated) · spine init→archive, 1 crew gate (g1: implement + review + integrate) · subagent tiers: sonnet (cold plan critic), opus (implementer), opus (reviewer)

**Instruction adherence:** fully followed
- Drove the full spine through the engine; no step done outside the checklist. Reconciled the ask against the frozen launch order (no human), satisfied the four `user-decision` checkpoints by citing launch-order sections. Both triage candidates routed recommend-and-defer (new-issue filing floated to Admiral per Inherited Latitude).

**Friction / unclear:**
- Engine verb ordering: several steps required attesting a null-check PRECONDITION (`p1`) BEFORE `start`, whereas postconditions are attested AFTER `start`. The refusal message ("preconditions unmet") is clear once seen, but the asymmetry cost one extra round-trip per step (init/plan/understand/execute/g1-*). Not a defect — a doc line "attest null preconditions before `start`" in the engine reference would remove the stumble.
- `advance` requires a `--why` running-understanding on every non-mechanical gate. Good for cold-start resumability; worth knowing up front so the first `advance` doesn't get refused.

**Crew-reported friction:**
- Implementer AND reviewer both flagged the same handoff gap: the "full suite green" close criterion did not warn that three EXISTING fixtures (`test_meta_json_written_incrementally_launch_then_final`, `test_resume_recovers_killed_runner_mid_measurement`, `test_final_meta_preserves_launch_liveness_fields`) hand-seed the corpus id via the raw primitive and would break when the assert-site id changed — the implementer had to discover and migrate them. This is exactly the case `IMPLEMENTER_HANDOFF.template.md:27` already tells the Commander to pre-empt ("when the behavior change invalidates an existing test's scenario, name that test and say so explicitly"). Doctrine already covers it; the miss was mine in authoring the handoff — I under-enumerated the hand-seeded fixtures because I scoped the diff by the production sites, not by every test that seeds the changed value. Applied-in-reflection: when a change alters a value that tests SEED (not just assert), grep for every seeder before freezing the handoff.

**What worked well (kept for signal):**
- The cold plan critic earned its keep decisively: it caught the anchor-rule BLOCKER (the stable-id function must anchor on the ORIGINAL install root, not the tree being hashed — otherwise the copy-based assert site no-ops and false-fences EVERY run) BEFORE implementation. Left unspotted, that would have shipped a fix that silently broke every eval run and surfaced only late. Strong confirmation of the design-it-twice/cold-critic doctrine on correctness-sensitive changes.
