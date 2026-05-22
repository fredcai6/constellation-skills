# Subagent Handoff

## Role
`<implementer | reviewer | cartographer | triage | etc.>`

## Task
`<one bounded task>`

## Intent
`<why this task exists / what future state it supports>`

## Authority

- **Explicit user decision:** `<decision or none>`
- **Existing project ground rule:** `<rule or none>`
- **Conductor decision:** `<decision or none>`
- **Conservative default:** `<default or none>`
- **Unresolved assumption:** `<assumption or none>`

## Allowed scope
`<files, regions, artifacts, or decisions this agent may touch>`

## Forbidden scope
`<what this agent must not change, decide, or inspect unless blocked>`

## Required context
- `<doc/packet/rule/handoff>`

## Critical rules
- `<task-specific rule>`

## Expected outputs
`<diff, packet, review, recommendation, tests, etc.>`

## Required evidence
`<tests, commands, inspection notes, generated artifact status>`

## Stop conditions
Stop and return if scope is exceeded, new architecture decision is required, evidence cannot be produced, glossary ambiguity appears, or dependency/failure policy decision is needed.

## Return format
`<structured response expected>`
