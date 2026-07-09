# Constellation Overview

```text
Charter      -> interrogates engineering doctrine and compiles agent-operable context
Admiral      -> runs an epic as the human's delegate; dispatches Commanders in waves; adjudicates, merges, and harvests at closeout
Commander    -> runs one bounded issue end to end; owns spine, interrogation, and execute checklists; dispatches crew
Workbench    -> manages recoverable workflow state and drives the checklist engine
Interrogator -> questions request/design ambiguity as a survey probe
Cartographer -> maintains current-only structural map
Scout        -> audits map-first architecture pressure
Implementer  -> implements a bounded change from a handoff
Reviewer     -> independently verifies a bounded change
Triage       -> classifies and writes issue-ready recommendations; no checklist
Lessons-auditor -> distills scoped, grounded lesson candidates from run artifacts with fresh context (Admiral closeout / Commander feedback subagent)
Docent       -> generates a stamped static HTML explainer site from Cartographer map truth; read-only map consumer
```

The checklist engine (`scripts/checklist_engine.py`, schema `docs/CHECKLIST_SCHEMA.md`, model `docs/CHECKLIST_ENGINE_DESIGN.md`) is the substrate every role drives: a `gated` (execution) or `survey` (verification/inquiry) plan worked one step at a time, with the human as the top tier surfacing decisions at Commander checkpoints.

## Relationship Contract

Skill.md is trigger, boundary, and resource pointer. Templates are the interface. References hold doctrine/detail.

| Producer | Artifact/interface | Consumer | Contract |
|---|---|---|---|
| Skills (`_shared`, bundled at install) | `references/global-{everyone,orchestrator,crew}.md` | all roles | inherited approach doctrine read first at each checklist's context step; identical across projects; the home for general-workflow `constellation` lessons |
| Commander | `.agent-work/<work-id>/spine.json` (gated) | Cartographer, Interrogator, human | one bounded issue: understand/plan/execute/cleanup; drives interrogation and gate plan; human verifies at checkpoints |
| Commander | `.agent-work/<work-id>/execute.json` (gated) | Implementer, Reviewer | frozen gate plan authored at plan time; three tasks per gate (implement/review/integrate); not edited mid-run |
| Charter | `docs/agents/ORCHESTRATOR_CONTEXT.md` | Commander, Cartographer, Scout | project DELTAS over inherited global-orchestrator doctrine: planning, authority, evidence, stop/ask departures |
| Charter | engine config (rework cap, replan policy, human checkpoints) | Commander, Workbench engine | sets the mechanism limits the engine enforces |
| Charter | `docs/agents/CREW_CONTEXT.md` | Crew | project DELTAS over inherited global-crew doctrine: implementation/review rules usable inside a handoff |
| Charter | `docs/agents/GLOSSARY.md` | all roles | shared terms only; no workflow state |
| Charter | `docs/agents/AGENT_GUIDE.md` + root `AGENTS.md`/`CLAUDE.md` pointers | all agents (Constellation or external) | single repo-orientation guide: layout, documentation map, conventions; the shared middle of the two contexts, not how to approach the job |
| Commander | `.agent-work/AGENT_FEEDBACK.md` | future Charter refresh, maintainers | unified run retrospective appended before archive; persists across work-ids; workflow-improvement signal, not project truth |
| Workbench | `templates/DEFAULT.template.json` | any role | generic gated controller for ad-hoc work; not durable truth |
| Role skills | role-specific checklist templates | owning role, Workbench | execution controller when role ships one; Workbench creates/archives files but does not own semantics |
| Workbench | closeout/archive rules | Commander, Cartographer | artifact hygiene; roles execute package movement at closeout |
| Interrogator | `.agent-work/<work-id>/interrogation.json` | Commander, Charter | survey of questions; consolidates to a resolved understanding |
| Cartographer | `docs/architecture/packets/` + `index.md` | Scout, Commander, Implementer, Reviewer, Docent | current structural truth and sparse purpose/constraint/rationale anchors |
| Cartographer | mismatch/Triage candidate | Commander, Triage | current-vs-future separation with structural anchor |
| Scout | `SCOUT_REPORT` | user, Commander, Triage | ranked architecture improvement candidates with map/code evidence |
| Commander | `IMPLEMENTER_HANDOFF` | Implementer | bounded task, authority, scope, exclusions, test mode, evidence requirements, stop conditions |
| Commander | `REVIEWER_HANDOFF` | Reviewer | task statement, diff access, close criteria, constraints, implementer evidence |
| Implementer / Reviewer | `IMPLEMENTER_RESULT` / `REVIEW_RESULT` | Commander | evidence, blockers, scope drift, assumptions, out-of-scope observations |
| Commander, Cartographer, Scout, Implementer, Reviewer | Triage candidate | Triage | future work package, not current-scope expansion |
| Triage | issue-ready recommendation | user / issue tracker | bounded future work with evidence and acceptance criteria |

## Context separation

Two orthogonal axes. **Audience:** high-level (orchestrator) agents use project purpose, user intent, structural map packets, glossary, and workflow state; low-level (crew) agents receive bounded task, allowed scope, critical rules, relevant structural packet, required evidence, and stop conditions. **Source:** each agent reads its inherited *global* doctrine (bundled with the skill at `references/global-{everyone,<tier>}.md`, identical across projects) first, then the project's thin *local* deltas (`docs/agents/*`, read if present) — layered, never merged. The global buckets hold the approach baseline; the project files hold only departures.

## Truth layers

```text
Code, tests, configs, generated behavior:
  dense truth

Structural map packets, agent context, glossary:
  compressed durable truth

Commander execute.json (frozen gate plan), crew handoffs, default checklists:
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
