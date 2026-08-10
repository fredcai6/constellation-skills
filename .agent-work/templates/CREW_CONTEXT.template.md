# Crew Context — project deltas

**Deltas over inherited global doctrine.** Implementation and review discipline, required handoff fields,
the result-is-the-deliverable rule, and the generic block/stop criteria are inherited from
`references/global-crew.md` and `references/global-everyone.md` and must NOT be restated here. This file
carries only project-specific rules that change implementation or review. Omit any section with no project
delta.

Agent-facing context. Use bullets, tables, and fragments. Omit prose that does not change agent action.

## Project Purpose

`<What this project exists to do. Include what it explicitly is not trying to do.>`

## Scope And Exceptions

`<Omit when context applies cleanly to the whole repo. Include only partial coverage or material subsystem differences.>`

## Subsystem Rigor (deltas)

| Subsystem | Rigor profile | Execution context | Crew implication |
|---|---|---|---|
| `<subsystem>` | `<profile>` | `<context>` | `<implementation/review rule>` |

## Implementation Rules

- `<project-specific implementation rule: naming/labeling conventions, in-file documentation strategy, module shape>`
- `<project-specific implementation rule>`

## Interface And Contract Rules

- `<interface shape, validation, config, or contract rule>`
- `<status/error return convention where material>`

## Failure And Reporting Rules

`<Include only where the project departs from the global fail-visibly / no-hidden-fallback default.>`

**Default failure policy:** `<fail-visibly mechanism by execution context>`  
**Fallback policy:** `<forbidden | explicit only | allowed with evidence | other>`  
**Degraded output policy:** `<none | visibly labeled | status/event required | other>`  
**Required reporting mechanism:** `<status object | event code | log | audit record | none>`

## State, Side Effects, And Determinism

- `<state/side-effect rule>`
- `<determinism/randomness rule; units/frames/identity rule if material>`

## Evidence Requirements (project additions beyond the global baseline)

- `<project-specific evidence beyond generic test-led execution>`
- `<no-test-surface artifact categories and required review evidence, if project-specific>`

## Documentation, Dependency, Security (project)

- `<project-specific docs/contracts/context update rule; generated-artifact rule if material>`
- `<dependency approval/evidence rule; canonical command only if truly project-wide>`
- `<secret/private data rule; public or user-facing claim evidence/wording rule>`

## Review Block Criteria (project-specific, beyond the global blockers)

- `<project-specific blocker>`
- `<project-specific blocker>`

## Compromise Policy (project)

- `<accepted compromise tracking or blocking rule; exit-condition requirement if material>`
