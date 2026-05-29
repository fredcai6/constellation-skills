# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`<gate id/title>`

## Completed slice
`<what changed>`

## Scope
**Files changed:**
- `<path>`

**Specific exclusions touched:** `<no | yes + explanation>`

## Behavior changed
`<yes/no + summary>`

## Test mode
**Required:** `<test-first | test-after | evidence-only | none>`  
**Satisfied:** `<yes/no + reason>`

## Evidence

```bash
<command>
```

**Result:** `<pass/fail/not run + reason>`

## TDD evidence, if required

- Failing test observed: `<command/output>`
- Passing test observed: `<command/output>`
- Refactor while green: `<yes/no>`

## Docs/contracts touched
- `<path or none with reason>`

## Assumptions
- `<assumption or none>`

## Stop conditions hit
- `<condition or none>`

## Out-of-scope observations
- `<finding for Pilot or none>`

## Return status
`complete | partial | blocked | out-of-scope | failed`
