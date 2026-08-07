# Mission Frame

Map-first frame for the bounded issue. Author this from the **current map** before authoring `execute.json`. Concise fragments; omit a field when the map carries nothing for it.

Skip or shrink this frame for a trivial local/mechanical change where the map adds nothing — the map is context, not authority over code. State that judgement in **Intent** when you skip it.

## Intent
`<the bounded outcome this run must achieve, in map terms>`

## Affected Capabilities
`<capability: nodes this run changes or relies on — the primary behavior anchors>`
- `<capability:id — what it does now, how this run touches it>`

## Examples / Events
`<concrete examples under those capabilities, and event: nodes emitted/consumed, only if relevant>`
- `<example or event:id — why it matters to this run>`

## Structural Anchors
`<struct: nodes (and their level) the work lands in or depends on>`
- `<struct:id — path/symbol, level>`

## Governing Constraints / Assumptions
`<constraint:/assumption: nodes that govern the affected structure — must not be silently violated>`
- `<constraint:id | assumption:id — what it requires, what breaks if ignored>`

## Decision Anchors & Decision Pressure
`<decision: anchors (explained-by) already governing this structure, and new choices this run forces>`
Grade every anchor with an `@grade` child line — the tier tells a gate whether it may revise the decision
in place or must stop and float (see `references/global-everyone.md`, "Decision fixedness"):
```
- decision:md-decision-is-a-list-item — only list items are decisions; prose never is.
  @grade: settled/measured · leans g1-implement · settle: lint the real templates, confirm the intro prose is not flagged
- decision:output-shape — the batched-objections view ends in one question.
  @grade: guess · leans g2-doctrine · settle: show one rendered report to the approver, keep or trim
```
Decision **pressure** is a choice not yet made, so it carries no grade — it is a candidate to surface, not an anchor.
- `<decision:id — what it fixed>`
  `@grade: <tier>[/provenance][ · leans <ids>][ · settle: <experiment>]`
- `<decision pressure: a choice this run will force to the human as a decision candidate — see SKILL "Decision candidates">`

## Claims / Evidence Surfaces
`<claim: nodes (verified-by) and the checks/evidence that back the affected behavior; what evidence each gate should re-confirm>`
- `<claim:id — assertion and how it is checked>`

## Map Confidence / Staleness / Disputes
`<map areas touching this run that are low-confidence, partial, stale, or disputed>`
- `<node id — status/confidence, and how it alters the plan: scout/verify step, or surface as a decision — do NOT silently trust>`

## Out of Scope
`<capabilities, structures, or constraints deliberately untouched, to keep the run bounded>`
