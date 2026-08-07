# Replan v1 contracts

## Contents

- [Input](#input)
- [Result](#result)
- [Preservation and escalation](#preservation-and-escalation)
- [Completion](#completion)

## Input

`REPLAN_INPUT` contains the exact G1 `current_plan`, completed outcomes, at
least one wave-evidence observation, classified discrepancies, a complete
completed/open partition of current-wave issue identities, unlaunched item
identities and kinds, and repository anchors/map status. Arrays may be empty
only where the template and verifier permit it. Unknown fields, duplicate
identities, wrong types, and invalid enums fail fast.

Discrepancy classifications map to one disposition action:

- `blocks_current_wave_exit` → `repair_current_wave`
- `invalidates_forecast_or_decomposition` → `revise_plan`
- `later_only` → `amend_forecast_or_parked`
- `evidence_only` → `record_evidence_only`
- `drop` → `drop`

## Result

`REPLAN_RESULT` records exactly one decision: `advance`, `repair`, `replan`, or
`stop`. Every input discrepancy and unlaunched identity receives exactly one
disposition. Evidence-only and dropped discrepancies never claim issue
creation. A rewrite replacement is required only for `rewrite`, and its shape
is discriminated by the input item kind using the exact G1 issue, forecast,
uncertainty, or parked shape.

Only `stop` may set `current_wave` to null. `repair` preserves the current wave
and forecast exactly. Non-null waves and all revised forecast/uncertainty/parked
values retain the strict G1 shapes.

## Preservation and escalation

An applicable result preserves every open launched issue exactly. Fixed
boundaries are `intent_and_why`, `definition_of_done`, `good_enough`,
`hard_constraints`, and `fixed_decisions`. A material change on one of those
surfaces requires `applicable=false` and an escalation with a boundary-typed
`proposed_value`, nonempty reason, and named authority. It is a proposal, never
an applied plan mutation. Because v1 has one singular escalation object, one
packet may propose changes to only one distinct fixed boundary; split proposals
that cross fixed boundaries into separate packets.

Code validates invariants, not planning judgment. It does not score confidence,
choose the exit, create tracker issues, or infer a portfolio policy.

## Completion

The pass is complete when input and result verify, every identity is
dispositioned, `wave_review_comment` and `revised_epic_body` are nonempty
Markdown, the offline renderer succeeds, and an independent reviewer accepts
the judgment and skill goodness.
