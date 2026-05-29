# Constellation Overview

```text
Charter      -> interrogates engineering doctrine and compiles agent-operable context
Commander    -> runs one bounded issue end to end; the human's rigor scaffold
Workbench    -> manages recoverable workflow state and drives the checklist engine
Interrogator -> questions request/design ambiguity as a survey probe
Cartographer -> maintains current-only structural map
Scout        -> audits map-first architecture pressure
Pilot        -> executes the frozen gate plan
Implementer  -> implements a bounded change from a handoff
Reviewer     -> independently verifies a bounded change
Triage       -> packages future work as issue-ready recommendations
```

The checklist engine (`scripts/checklist_engine.py`, schema `docs/CHECKLIST_SCHEMA.md`, model `docs/CHECKLIST_ENGINE_DESIGN.md`) is the substrate every role drives: a `gated` (execution) or `survey` (verification/inquiry) plan worked one step at a time, with the human as the top tier surfacing decisions at Commander checkpoints.

## Relationship Contract

Skill.md is trigger, boundary, and resource pointer. Templates are the interface. References hold doctrine/detail.

| Producer | Artifact/interface | Consumer | Contract |
|---|---|---|---|
| Commander | `.agent-work/<work-id>/COMMANDER_SPINE` (gated) | Pilot, Cartographer, Interrogator, human | one bounded issue: understand/plan/execute/cleanup; produces the frozen gate plan; one-shot; human verifies Commander steps |
| Charter | `docs/agents/ORCHESTRATOR_CONTEXT.md` | Pilot, Cartographer, Scout | project-specific planning, authority, evidence, stop/ask rules |
| Charter | engine config (rework cap, rigor checkpoints, rules root) | Commander, Workbench engine | sets the mechanism limits the engine enforces |
| Charter | `docs/agents/CREW_CONTEXT.md` | Crew | project-specific implementation/review rules usable inside a handoff |
| Charter | `docs/agents/GLOSSARY.md` | all roles | shared terms only; no workflow state |
| Pilot | `.agent-work/<work-id>/PILOT_CHECKLIST.md` | Pilot, Crew, Workbench | Pilot execution controller; framing/implementation/closing gates, evidence per implementation gate; not durable truth |
| Workbench | `.agent-work/<work-id>/DEFAULT_CHECKLIST.md` | Crew | fallback controller when no role-specific checklist exists; not durable truth |
| Role skills | role-specific checklist templates | owning role, Workbench | execution controller when role ships one; Workbench creates/archives files but does not own semantics |
| Workbench | closeout/archive rules | Pilot, Cartographer | artifact hygiene; roles execute package movement at closeout |
| Interrogator | `.agent-work/<work-id>/INTERROGATOR_QUESTIONS.md` | Charter, Pilot | live question queue, skipped items, answers, follow-ups |
| Cartographer | `docs/architecture/packets/` + `index.md` | Scout, Pilot, Crew | current structural truth and sparse purpose/constraint/rationale anchors |
| Cartographer | mismatch/Triage candidate | Pilot, Triage | current-vs-future separation with structural anchor |
| Scout | `SCOUT_REPORT` | user, Pilot, Triage | ranked architecture improvement candidates with map/code evidence |
| Pilot | `CREW_HANDOFF` | Crew | bounded task, authority, scope, exclusions, evidence, stop conditions |
| Crew | `IMPLEMENTER_RESULT` / `REVIEW_RESULT` | Pilot | evidence, blockers, scope drift, assumptions, out-of-scope observations |
| Pilot, Cartographer, Scout, Crew | Triage candidate | Triage | future work package, not current-scope expansion |
| Triage | issue-ready recommendation | user / issue tracker | bounded future work with evidence and acceptance criteria |

## Context separation

High-level agents use project purpose, user intent, structural map packets, glossary, and workflow state.

Low-level agents receive bounded task, allowed scope, critical rules, relevant structural packet, required evidence, and stop conditions.

## Truth layers

```text
Code, tests, configs, generated behavior:
  dense truth

Structural map packets, agent context, glossary:
  compressed durable truth

Pilot checklist (with embedded implementation gates), handoffs, default checklists:
  workflow-local truth

Issues:
  future work
```

## Authority transfer

Agent action traces to one of:

- explicit user decision
- existing project ground rule
- task-specific delegation
- named conservative default
- unresolved assumption

Only the first three are strong authority.
