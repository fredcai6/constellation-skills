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

## Evidence Produced
`<test output, command results, artifacts from IMPLEMENTER_RESULT — include pass/fail>`

## Suggested Model Tier
`<simple bounded | stronger — reason: scope/ambiguity/risk>`

## Stop Conditions
Stop and return BLOCK if: the diff cannot be accessed, evidence is absent or unverifiable, or a policy decision is required before a verdict is possible.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings, blockers, out-of-scope observations.
