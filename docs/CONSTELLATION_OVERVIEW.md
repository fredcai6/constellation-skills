# Constellation Overview

```text
Charter      -> interrogates engineering doctrine and compiles agent-operable context
Workbench    -> manages recoverable workflow state
Interrogator -> questions request/design ambiguity with traceable queue
Cartographer -> maintains current-only structural map
Scout        -> audits map-first architecture pressure
Pilot    -> shapes work and delegates execution
Crew         -> implements and reviews bounded changes
Triage       -> packages future work as issue-ready recommendations
```

## Relationship Contract

Skill.md is trigger, boundary, and resource pointer. Templates are the interface. References hold doctrine/detail.

| Producer | Artifact/interface | Consumer | Contract |
|---|---|---|---|
| Charter | `docs/agents/ORCHESTRATOR_CONTEXT.md` | Pilot, Cartographer, Scout | project-specific planning, authority, evidence, stop/ask rules |
| Charter | `docs/agents/CREW_CONTEXT.md` | Crew | project-specific implementation/review rules usable inside a handoff |
| Charter | `docs/agents/GLOSSARY.md` | all roles | shared terms only; no workflow state |
| Workbench | `.agent-work/<work-id>/LOCAL_TODO.md` | all roles | recoverable state; not durable truth |
| Workbench | closeout/archive rules | Pilot, Cartographer | artifact hygiene; no semantic workflow decisions |
| Interrogator | `.agent-work/<work-id>/INTERROGATOR_QUESTIONS.md` | Charter, Pilot | live question queue, skipped items, answers, follow-ups |
| Cartographer | `docs/architecture/packets/` + `index.md` | Scout, Pilot, Crew | current structural truth and sparse purpose/constraint/rationale anchors |
| Cartographer | mismatch/Triage candidate | Pilot, Triage | current-vs-future separation with structural anchor |
| Scout | `SCOUT_REPORT` | user, Pilot, Triage | ranked architecture improvement candidates with map/code evidence |
| Pilot | `GATED_PLAN` | Pilot, Crew | smallest independently stoppable gates with evidence and scope |
| Pilot | `CREW_HANDOFF` | Crew | bounded task, authority, scope, exclusions, evidence, stop conditions |
| Crew | `IMPLEMENTER_RESULT` / `REVIEW_RESULT` | Pilot | evidence, blockers, scope drift, assumptions, out-of-scope observations |
| Pilot, Cartographer, Scout, Crew | Triage candidate | Triage | future work package, not current-scope expansion |
| Triage | issue-ready recommendation | user / issue tracker | bounded future work with evidence and acceptance criteria |

## Context separation

High-level agents use project purpose, user intent, structural map packets, glossary, and workflow artifacts.

Low-level agents receive a bounded task, allowed scope, critical rules, relevant structural packet, required evidence, and stop conditions.

## Truth layers

```text
Code, tests, configs, generated behavior:
  dense truth

Structural map packets, agent context, glossary:
  compressed durable truth

Framing notes, gated plans, handoffs, local todos:
  workflow-local truth

Issues:
  future work
```

## Authority transfer

Agent action should trace to one of:

- explicit user decision
- existing project ground rule
- task-specific delegation
- named conservative default
- unresolved assumption

Only the first three are strong authority.
