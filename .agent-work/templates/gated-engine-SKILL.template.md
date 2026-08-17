---
name: constellation-<short-name>
description: <what ordered work this drives to completion>. Use when <triggering condition — ordered steps that must not be skipped>. Not <confusable skill> (<why different>).
invoker: <human | agent | both>
---

# Constellation <Title>

<Leading line: the ordered work this skill drives, in one sentence.>

Drive every step through the checklist engine and finish its sequence — final `advance`, then `release`, as journaled actions. **Work the engine never saw did not happen.** Full completion doctrine: `_shared/global-everyone.md`.

## Instantiate the plan

Build a `gated` plan from `templates/<NAME>_PLAN.template.json` and drive it. When this plan *is* the spine this process's door is bound to, drive it through the MCP door's `spine_status`/`spine_start`/`spine_advance`/`spine_evidence` tools (see workbench `references/checklist-engine.md` — MCP door). An in-session crew member driving its own plan beside the spine it was launched for is not that case: one door drives one spine at a time, and it refuses to rebind while its owner still holds that spine's lease, so the door cannot reach your plan at all. That is not a second-best path with a working primary behind it — such a plan is driven by this skill's bundled checklist engine, and by nothing else. One item per step, each with a real command or artifact postcondition. Ask the engine `current`, do exactly what the active step says, `advance` only when its checks pass.

## The gates

1. **<gate one>** — <imperative>; postcondition <check>.
2. **<gate two>** — <imperative>; postcondition <check>.
3. **<final gate>** — <imperative>; postcondition <check>. Then `release`.

## Rail + review

One mechanically-enforced rail: <the engine command postcondition that must pass>. An independent fresh-context reviewer judges quality the rail cannot; a defended rail exception needs the reviewer's co-sign + a log entry. Schema: `references/<x>.md`.
