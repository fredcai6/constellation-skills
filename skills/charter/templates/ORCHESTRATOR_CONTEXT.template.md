# Orchestrator Context

Project-specific overlay for Conductor and Cartographer. Generic role mechanics stay in the skills; this file contains only project rules that affect work shaping, architecture clarification, evidence expectations, and stop/ask behavior.

## Project Purpose

`<What this project exists to do. Include what it explicitly is not trying to do.>`

## Scope And Exceptions

`<Omit this section when context applies cleanly to the whole repo. Include only partial coverage or material subsystem differences.>`

## Operating Context

**Primary users:** `<who directly uses outputs>`  
**Primary decisions/actions supported:** `<what outputs influence>`  
**Output authority:** `<advisory | diagnostic | canonical record | user-facing claim | automated action | mixed>`  
**Failure consequences:** `<wrong | stale | missing | slow | misleading | unreproducible | unsafe | privacy leak | maintenance erosion | mixed>`

## Subsystem Rigor

| Subsystem | Rigor profile | Execution context | Orchestrator implication |
|---|---|---|---|
| `<subsystem>` | `<profile>` | `<context>` | `<planning/framing/evidence implication>` |

## Canonical Inputs And Data Sources

- `<input/source>`: `<when it is canonical and what agents must not bypass>`

## Engineering Rules

- `<project-specific correctness/evidence/interface/failure/state rule>`
- `<project-specific architecture boundary or documentation rule>`
- `<project-specific dependency/security/performance/generated artifact rule>`

## Evidence Expectations

- `<what evidence is enough for common work types>`
- `<what evidence is required for high-risk or public outputs>`

## Failure And Degraded Behavior

- `<fail-visible rule by execution context>`
- `<fallback/degraded-output rule>`

## Documentation And Generated Artifacts

- `<when context/docs/contracts must change>`
- `<how generated artifacts should be treated>`

## Compromise Policy

- `<what compromises are allowed, blocked, or require exit conditions>`

## Stop And Ask

Stop and ask when project context, user instruction, and observed artifacts conflict in a way that affects the task. Do not resolve conflicts by choosing an authority source by policy.
