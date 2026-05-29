# Workbench Checklist Engine

The engine is the deterministic state machine an agent transacts with **one step at a time**. It holds canonical state and enforces *mechanism* — ordering, evidence shape, the rework cap, the consolidation guard — and never judges quality. An agent does not re-read and self-manage a checklist; it asks the engine what to do, does it, and reports back.

Tool: `scripts/checklist_engine.py --file <checklist.json> <verb>`. Schema: `docs/CHECKLIST_SCHEMA.md`. Model: `docs/CHECKLIST_ENGINE_DESIGN.md`.

## One agent, one plan

A checklist is one plan one agent works through — not the whole hierarchy in one file. Delegation is **by reference**: a gate sets `child_checklist: <work-id>` pointing at a separate plan; the sub-agent drives its own checklist. Every agent (Commander, Pilot, implementer, reviewer) has its own.

## Two types

- **`gated`** — execution. Ordered; satisfy each item to advance; a failure **blocks** (rework). Used by the Commander spine, the Pilot gate plan, the implementer's own plan.
- **`survey`** — verification/inquiry. Visit every item; **append** more from context; a failure is **recorded, never blocks**; then **consolidate** into one result. Used by the reviewer (→ APPROVE/BLOCK + findings) and the Interrogator (→ resolved understanding).

## Verb loop

```
current                          # which step am I on (an imperative)
start <id>                       # begin it; engine checks preconditions
  ... do the work ...
advance <id>                     # gated: engine runs command checks / verifies artifact shape, then closes
record <id> --result pass|fail   # survey: record the check; never blocks
consolidate [--verdict ...]      # survey: every item visited -> hand up a result
```

Other verbs: `skip <id> --reason` (OBE), `block <id> --blocker ... --authority ... --next ...` (bubbles to parent), `reopen <id> --reason` (gated rework; escalates at the cap), `append <id> --title --imperative` (survey only), `attest <id> --cond <id>` (assert a qualitative precondition — trust but verify), `attach <id> --type --payload` (record evidence, e.g. a child survey's verdict), `flag-candidate --from <id> --statement` (out-of-scope discovery).

## Obey refusals

The engine answers illegal moves with an imperative, e.g. `REFUSED: g1: postconditions unmet ['c1']`. Treat that as the next instruction — fix the named gap, do not work around it. The refusal *is* the gate.

## Mechanism the engine guarantees

- **Ordering** — cannot start a later gate before the active one (gated).
- **Evidence shape** — `command` postconditions must exit 0; `artifact` postconditions need a matching evidence item present. Quality is judged by the reviewer/human, not the engine.
- **Rework cap** — `reopen` counts; on the (cap+1)th it stops re-dispatching and escalates to the parent. The cap is set at Charter time.
- **Consolidation guard** — `consolidate` refuses `APPROVE` while any item is `fail`, unless an explicit `--override-reason` is given.

## Bubble-up channels

`triage_candidates` (out-of-scope work to capture; Triage drains them at clean-up) and `blockers` (stuck items needing authority). Both surface to the **parent agent** first; the parent escalates to the human only if it cannot resolve them.
</content>
