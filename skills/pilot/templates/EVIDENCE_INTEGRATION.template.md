# Evidence Integration

## Gate
`<gate name>`

## Crew Result

**Role:** `<implementer | reviewer>`  
**Status:** `complete | partial | blocked | out-of-scope | failed`

## Implementation Evidence
- `<tests, commands, diff inspection, generated output, or none because reviewer-only gate>`

## Review Evidence
- `<handoff compliance, code/doc quality, blocker status, or none because implementer-only gate was explicitly approved>`

## Required Evidence Check
`<satisfied | missing | contradicted>`

Implementation gates require both implementation evidence and review evidence before gate close, unless review was explicitly skipped with reason. Do not batch review at final closeout.

## Original Intent Check
`<evidence still satisfies Intent Protected | concern>`

## Scope Drift Check
`<in allowed scope | scope concern | scope exceeded | specific exclusion touched>`

## Assumption Check
`<still holds | changed | now blocking | none>`

## Reviewer Approval Check
Reviewer approval alone is insufficient. Record whether reviewer checked handoff compliance, quality, blockers, and evidence.

## New Information
- `<new ambiguity / decision / structural change / Triage candidate / none>`

## Architecture Reconciliation Implication
`<no action | Pilot packet edit | request Cartographer verification | collect Triage candidate>`

## Pilot Decision
`continue | ask user | send back to Crew | request Cartographer verification | revise gated plan | collect Triage candidate | close out`

## Reason
`<why>`

## Plan / Checklist Updates Required
- `<update>`
