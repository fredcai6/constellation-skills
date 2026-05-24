# Crew Handoff

Agent-to-agent context. Use concise fragments; omit filler.

## Role
`implementer | reviewer`

## Assigned Gate
`<gate id/name>`

## Suggested Model Tier
`<simple bounded | stronger broad/ambiguous, because scope/risk/review complexity>`

## Test Mode
`<same as plan | TDD required | test-after allowed | inspection-only, because <reason>>`

## Task
`<one bounded task>`

## Intent Protected
`<user/system outcome this gate must preserve>`

## Close Criteria
`<truth required for this gate to close>`

## Authority
`<user decision | project rule | Conductor decision | assumption needing confirmation>`

## Allowed Scope
`<files, regions, artifacts, or decisions this Crew role may touch>`

## Specific Exclusions
`<tempting in-scope-looking files, areas, or decisions that must not be touched; omit if none>`

## Relevant Project Rules For This Gate
- `<distilled rule from Charter/Orchestrator/Crew context>`

## Required Context
- `<artifact/file Crew must inspect; omit if none>`

## Project Mechanics For This Gate
`<none | issue comment required | commit required | do not commit | ask before repo action>`

## Required Evidence
`<tests, commands, inspection notes, generated artifact status, review result>`

## Required Verification Commands
`<commands or none with reason>`

## No-Test-Surface Rationale
`<only when test mode says inspection-only/no-test>`

## Stop Conditions
Stop and return if allowed scope is exceeded, a specific exclusion must be touched, evidence cannot be produced, hidden intent would need inference, or an authority/dependency/failure policy decision is needed.

## Return Format
`<diff summary, evidence, blockers, scope concerns, assumptions used>`
