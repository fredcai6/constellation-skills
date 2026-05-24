# Crew Context

Project-specific overlay for Crew implementer/reviewer behavior. Generic execution discipline stays in the skill; this file contains only project rules that change implementation or review.

## Project Purpose

`<What this project exists to do. Include what it explicitly is not trying to do.>`

## Scope And Exceptions

`<Omit this section when context applies cleanly to the whole repo. Include only partial coverage or material subsystem differences.>`

## Subsystem Rigor

| Subsystem | Rigor profile | Execution context | Crew implication |
|---|---|---|---|
| `<subsystem>` | `<profile>` | `<context>` | `<implementation/review rule>` |

## Implementation Rules

- `<project-specific implementation rule>`
- `<project-specific implementation rule>`

## Interface And Contract Rules

- `<interface shape, validation, config, or contract rule>`
- `<status/error return convention where material>`

## Failure And Reporting Rules

**Default failure policy:** `<fail visibly mechanism by execution context>`  
**Fallback policy:** `<forbidden | explicit only | allowed with evidence | other>`  
**Degraded output policy:** `<none | visibly labeled | status/event required | other>`  
**Required reporting mechanism:** `<status object | event code | log | audit record | none>`

## State, Side Effects, And Determinism

- `<state/side-effect rule>`
- `<determinism/randomness rule>`
- `<units/frames/identity rule if material>`

## Evidence Requirements

**Behavior changes:** `<project-specific evidence beyond generic test-led execution>`  
**Bug fixes:** `<regression evidence>`  
**Interface/contract changes:** `<contract/caller evidence>`  
**Generated artifacts:** `<regenerate/check/review evidence>`  
**No relevant test surface:** `<artifact categories and required review evidence>`

## Documentation Rules

- `<project-specific docs/contracts/context update rule>`
- `<generated artifact documentation rule if material>`

## Dependency And Tooling Rules

- `<dependency approval/evidence rule>`
- `<canonical command only if truly project-wide>`

## Security, Privacy, And Publicness

- `<secret/private data rule>`
- `<public or user-facing claim evidence/wording rule>`

## Compromise Policy

- `<accepted compromise tracking or blocking rule>`
- `<exit-condition requirement if material>`

## Review Block Criteria

Block when:

- `<project-specific blocker>`
- `<project-specific blocker>`
- task instructions, context, tests, docs, or observed behavior conflict in a way that affects implementation or review

## Stop And Report

Stop and report when task authority is exceeded, required evidence cannot be produced, a material rule is ambiguous, a boundary or contract decision is needed, or project context conflicts with observed behavior.
