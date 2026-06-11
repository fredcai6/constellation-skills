# Reviewer Handoff

Concise fragments. Omit filler.

## Gate
`<gate id from execute.json, e.g. g1>`

## What Was Implemented
`<brief description of the change>`

## How to Inspect the Diff
`<exact diff command, commit range, or branch — how to see what changed>`

## Task Statement
`<the original task the implementer was given — what it was supposed to build>`

## Close Criteria
`<conditions required for APPROVE; each becomes a review check>`
- `<criterion>`

## Allowed Scope
`<what the implementation was permitted to touch>`

## Specific Exclusions
`<anything that was off-limits; flag if touched>`

## Constraints the Implementation Must Respect
`<rules inherited from the gate plan; each becomes a review check>`
- `<rule>`

## Map Anchors (inbound)
Map context this gate inherits from the mission frame; review the change against these so it lands on the right structure and honors recorded rules. Omit a line when the gate carries nothing for it.
- **Structural:** `<struct:id — path/symbol, level — where the work lands or depends>`
- **Capability:** `<capability:id — behavior this gate changes or relies on>`
- **Constraints/assumptions:** `<constraint:id | assumption:id — verify it was not silently violated>`
- **Decision anchors:** `<decision:id — governs this structure; flag any contradiction as a decision candidate>`
- **Evidence expectations:** `<claim:id or check this gate must re-confirm>`
- **Map confidence flags:** `<node id — low-confidence/stale/disputed area; confirm rather than trust; omit if none>`

## Evidence Produced
`<test output, command results, artifacts from IMPLEMENTER_RESULT — include pass/fail>`

## Suggested Model Tier
`<simple bounded | stronger — reason: scope/ambiguity/risk>`

## Stop Conditions
Stop and return BLOCK if: the diff cannot be accessed, evidence is absent or unverifiable, or a policy decision is required before a verdict is possible.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings, blockers, out-of-scope observations, workflow feedback (what in this handoff or the workflow made the review harder than it needed to be).
