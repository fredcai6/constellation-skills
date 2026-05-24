# Subagent Handoff

## Role
`<implementer | reviewer | cartographer | triage | etc.>`

## Mandate
`<bounded execution | bounded review | broad review | architecture/context task>`

## Suggested model tier
`<simple bounded | stronger broad/ambiguous, because <reason>>`

## Test mode
`<TDD required | test-after allowed | no test required, because <reason>>`

## Task
`<one bounded task>`

## Intent
`<why this task exists / what future state it supports>`

## Success criteria
`<done condition and acceptance criteria>`

## Authority

- **Explicit user decision:** `<decision or none>`
- **Existing project ground rule:** `<rule or none>`
- **Conductor decision:** `<decision or none>`
- **Conservative default:** `<default or none>`
- **Unresolved assumption:** `<assumption or none>`

## Allowed scope
`<files, regions, artifacts, or decisions this agent may touch>`

## Specific exclusions
`<rare explicit files, areas, or decisions that may seem in scope but must not be touched; omit if none>`

## Required context
- `<doc/packet/rule/handoff>`

## Critical rules
- `<task-specific rule>`

## Expected outputs
`<diff, packet, review, recommendation, tests, etc.>`

## Required evidence
`<tests, commands, inspection notes, generated artifact status>`

## Required verification commands
`<commands or none with reason>`

## No-test-surface rationale
`<only when test mode says no test required>`

## Stop conditions
Stop and return if scope is exceeded, new architecture decision is required, evidence cannot be produced, glossary ambiguity appears, or dependency/failure policy decision is needed.

## Return format
`<structured response expected>`
