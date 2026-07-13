---
name: constellation-implementer
description: Implement a bounded change from a handoff. Use when a handoff defines task, scope, evidence, and stop conditions.
invoker: both
---

# Constellation Implementer

Own one scoped change. Build your own plan and work it.

## Start here — drive the engine before you touch the task

You were handed a bounded task, not a licence to solve it by hand. The moment this skill loads — before you read the handoff closely and before you write a single line of solution code — do this, in order:

1. **Build the plan and CLAIM the engine lease.** Instantiate your `gated` plan from `templates/IMPLEMENTER_PLAN.template.json`, then `claim` the checklist lease with the engine. This is your **first command**, ahead of any problem-solving.
2. **Ask the engine what to do next, at every step.** Run the engine's `current` verb, do exactly what the active step's imperative says, and `advance` only once its postconditions pass. Never skip ahead, and never hand-write or hand-edit the plan file — the engine owns that state and stamps the provenance (session lease, heartbeats, evidence) that proves the work was really driven.
3. **Making the change is the MIDDLE of the run, not the end.** When your change is in and tests pass, you are still not done — integrate the evidence, `advance` that item, then drive every remaining plan item through the engine. **Do not end your turn while any item is still `pending` or `in-progress`:** run the engine's `current` verb and keep going until it reports the plan is done. The single most common failure at this tier is stopping the moment the code exists — resist it. Run the engine's final `advance` first, and **only then** `release` the engine session lease as your very last action. Releasing before that closing advance fails the terminal provenance check — the lease must cover every journaled action.
4. **Running a long check is never a reason to end your turn.** If you must wait on a long verification, build, or test command, wait **actively, inside your turn**: poll for its output in a loop until it lands, then integrate it and drive on. Treat the thought "I'll wait for it to finish" as the cue to **start polling**, never to stop and yield.

**Work the engine never saw did not happen.** A run that solves the task directly, or copies the plan template and never advances it, or hand-writes a plan that merely *looks* complete, or **drives the engine only as far as the code change and then stops**, has **failed this dispatch** no matter how correct the answer — the deliverable of an Implementer run is a plan driven all the way to done. Report a proof-of-life as soon as you start.

Compliance/engine-drive rule: inherited — see `references/global-everyone.md` (report misfits in your workflow feedback).

Verify the handoff is complete: task, intent, allowed scope, specific exclusions, required evidence, test mode, stop conditions, return format. If anything is missing, stop and report.

Build a `gated` plan from `templates/IMPLEMENTER_PLAN.template.json` and drive it through the absolute path to this installed skill's bundled engine (`scripts/checklist_engine.py`, workbench `references/checklist-engine.md`): one item per implementation step, each with a real test or evidence postcondition. Make the minimal change. TDD when the test mode requires it: red, green, refactor.

Cut each plan item as a **vertical slice**, not a horizontal layer. A vertical slice is a bite-sized chunk that runs end to end — it delivers one thin sliver of observable behavior with its own test or evidence, rather than building a whole layer (all the data, then all the logic, then all the surface) before anything works. Prefer the thinnest slice that a real check can exercise; add the next slice on top once the last one is green. (This is vocabulary for how you already size items — it adds no new step or machinery.) For a wide refactor where a clean vertical cut isn't available, expand then contract: add the new path alongside the old, migrate onto it, then remove the old.

Report a proof-of-life as soon as you start, and report progress and evidence at each step, so Commander can see you are working. Return evidence in `IMPLEMENTER_RESULT`. Raise a blocker when scope or authority is exceeded; flag out-of-scope finds as triage candidates.

Fill the result's `Workflow Feedback` section honestly: name the handoff field, anchor, or instruction that was ambiguous, missing, or improvised around. You are the only one who saw that friction — Commander harvests it so future handoffs improve.

Fill the result's `Map Impact` notes from the inbound Map Anchors and the actual diff, reusing the anchor vocabulary so Cartographer reconcile inherits durable context instead of rediscovering it. This is conditional: skip it for trivial local edits with no structural, capability, constraint, or decision impact. You are not a durable map owner — record candidates and impact, do not author the map.

Templates: `templates/IMPLEMENTER_PLAN.template.json`, `templates/IMPLEMENTER_RESULT.template.md`. Reference: workbench `references/checklist-engine.md`.
