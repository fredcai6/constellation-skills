# Implementer Handoff

Concise fragments. Omit filler.

## Gate
`<gate id from execute.json, e.g. g1>`

## Task
`<one bounded task — what to build>`

## Protected Intent
`<the user/system outcome this gate must not violate>`

## Test Mode
`<TDD required | test-after allowed | inspection-only — brief reason>`

## Close Criteria
`<what must be true when done; each item the implementer proves>`
- `<criterion>`

## Allowed Scope
`<files, modules, regions, or decisions the implementer may touch>`

## Specific Exclusions
`<things that look in-scope but are off-limits; omit section if none>`

## Constraints
`<rules the implementation must respect — from project rules or gate-specific needs>`
- `<rule>`

## Required Evidence
`<what to produce: test output, command result, inspection note, generated artifact>`

## Verification Commands

Exact commands to run. Write `none — <reason>` if not applicable.

```bash
<command>
```

## Suggested Model Tier
`<simple bounded | stronger — reason: scope/ambiguity/risk>`

## Authority
`<decisions already made and by whom; what the implementer must not decide alone>`

## Stop Conditions
Stop and return if: allowed scope must be exceeded, a specific exclusion must be touched, required evidence cannot be produced, a decision outside the given authority is needed.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence produced, assumptions used, stop conditions hit, out-of-scope observations.
