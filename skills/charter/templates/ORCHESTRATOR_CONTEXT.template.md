# Orchestrator Context — project deltas

**Deltas over inherited global doctrine.** The approach baseline — rigorous default posture, map-first
shaping, handoff completeness, gating and stop/ask — is inherited from `references/global-orchestrator.md`
and `references/global-everyone.md` and must NOT be restated here. This file carries only project-specific
facts and the points where this project **departs** from that baseline. Omit any section with no project
delta.

Agent-facing context. Use bullets, tables, and fragments. Omit prose that does not change agent action.

## Project Purpose

Owned by `docs/agents/AGENT_GUIDE.md` § Why This Exists — every agent reads it there, not here. Do not
restate it. This file starts at the stakes.

## Scope And Exceptions

`<Omit when context applies cleanly to the whole repo. Include only partial coverage or material subsystem differences.>`

## Operating Context

**Primary users:** `<who directly uses outputs>`  
**Primary decisions/actions supported:** `<what outputs influence>`  
**Output authority:** `<advisory | diagnostic | canonical record | user-facing claim | automated action | mixed>`  
**Failure consequences:** `<wrong | stale | missing | slow | misleading | unreproducible | unsafe | privacy leak | maintenance erosion | mixed>`

## Subsystem Rigor (deltas from the rigorous default)

| Subsystem | Rigor profile | Execution context | Orchestrator implication |
|---|---|---|---|
| `<subsystem>` | `<profile — and how it relaxes/strengthens the default>` | `<context>` | `<planning/framing/evidence implication>` |

## Repo Action Authority

**Commit sensitivity:** `<ask always | commit local ok | push ok | PR only | direct main allowed | custom>`  
**Commit archived work packages:** `<yes | no | ask each closeout>`  
**Commander may open PRs directly:** `<yes | no | ask first>`  
**Commander may merge to main:** `<yes | no | ask first>`

## Canonical Inputs And Data Sources

- `<input/source>`: `<when it is canonical and what agents must not bypass>`

## Evidence And Verification Map

`<Omit when there are no area-specific evidence rules. Area-specific commands belong in handoffs, not here.>`

| Area/subsystem | Required evidence | Handoff implication |
|---|---|---|
| `<area>` | `<evidence or command>` | `<what must be copied into handoff>` |

## Architecture And Scope Constraints

- `<planning/framing rule for ownership, cross-boundary work, canonical paths, or architecture clarification>`

## Project Engineering Rules (departures only)

- `<project-specific correctness/evidence/interface/failure/state rule that differs from the global baseline>`
- `<project-specific documentation, dependency, security, performance, or generated-artifact rule>`

## Compromise Policy (project)

- `<what compromises are allowed, blocked, or require exit conditions beyond the global default>`
