---
name: constellation-charter
description: Interrogate engineering doctrine and compile agent-operable Orchestrator, Crew, and Glossary context. Use when starting or refreshing repo agent context, engineering posture, standards, or shared terminology.
---

# Constellation Charter

## Purpose

Charter elicits the project's engineering doctrine and compiles it into role-operable context.

Final durable outputs:

```text
docs/agents/ORCHESTRATOR_CONTEXT.md
docs/agents/CREW_CONTEXT.md
docs/agents/GLOSSARY.md
```

Workflow-local outputs:

```text
.agent-work/<work-id>/CHARTER_CHECKLIST.md
.agent-work/CHARTER_OPEN_QUESTIONS.md
```

`CHARTER_OPEN_QUESTIONS.md` exists only while weak or unresolved Charter questions remain. Delete it during final compile.

## Use

Use when starting a repo, refreshing agent context, defining engineering posture, clarifying standards, or establishing shared human-agent terminology.

Do not use Charter to map architecture, plan a feature, review a diff, edit code/tests, create issues, or update non-agent project docs.

## Required Context

Fixed Constellation context:

```text
docs/CONSTELLATION_OVERVIEW.md
docs/OPERATING_PRINCIPLES.md
skills/conductor/SKILL.md
skills/cartographer/SKILL.md
skills/crew/SKILL.md
```

Target project context:

```text
docs/agents/*
AGENTS.md
README.md or equivalent project overview
philosophy/process docs
user-provided positive exemplars
```

Inspect code, tests, configs, or architecture docs only when a specific context decision needs light verification. Do not map the codebase.

## Fixed Boundaries

Charter informs Orchestrator context for Conductor and Cartographer, and Crew context for implementer/reviewer behavior.

Do not ask the user to redesign Constellation topology. If the fixed role model is a bad fit, the answer is to stop using these skills, not mutate Charter output.

Allowed writes:

```text
.agent-work/<work-id>/CHARTER_CHECKLIST.md
.agent-work/CHARTER_OPEN_QUESTIONS.md
docs/agents/ORCHESTRATOR_CONTEXT.md
docs/agents/CREW_CONTEXT.md
docs/agents/GLOSSARY.md
```

All other writes are out of Charter scope.

## Workflow Driver

Before asking Gate 0 questions, create or resume `.agent-work/<work-id>/CHARTER_CHECKLIST.md` from `templates/CHARTER_CHECKLIST.template.md`. Choose a date-plus-purpose work id unless the user supplied one or an obvious Charter folder exists.

The checklist is the only Charter todo and decision record. Do not create a separate decisions file.

Ask one decision question at a time. Gate 0 may request a small bundle of reference and exemplar paths because that is input collection, not a doctrine decision.

## Interrogation Rules

Start from `references/rigorous-default.md`. The user may accept, relax, or strengthen it by subsystem, but rigor is not opt-in.

Use `references/engineering-rubric.md` for required doctrine axes. Every axis must be touched. Mark an axis `not-material` only with user agreement.

A material decision affects future agent behavior, allowed scope, evidence requirements, failure behavior, interfaces/contracts, canonical inputs, documentation duties, dependency policy, security/privacy/publicness, performance/resource posture, generated artifacts, compromise policy, or stop/report conditions.

For each material decision, state:

```text
Default -> Cost -> Relaxation -> Scenario -> Decision -> Evidence
```

Do not accept slogans such as "do it right", "be careful", "use judgment", "write tests", "move fast", or "reasonable defaults". Convert them into a decision with cost, scenario, evidence, and role implication.

Record material decisions in the checklist with:

```text
Quality: strong | usable | weak | unresolved | not-material
Authority: user decision | accepted default | unconfirmed default | repo artifact | assumption
Posture: rigorous-default | relaxed | strengthened | mixed | not-applicable
```

Weak and unresolved decisions must remain visible in `.agent-work/CHARTER_OPEN_QUESTIONS.md` during provisional compile.

## Gate Order

1. Bootstrap references, Charter scope, and positive exemplars.
2. Classify operating context, execution context, output authority, failure consequence, and subsystem profile.
3. Interrogate engineering doctrine with the rubric.
4. Capture implementation conventions.
5. Resolve contradictions and excessive subsystem divergence.
6. Compile Orchestrator, Crew, and Glossary context.
7. Close out the checklist.

Do not optimize for one-session completion. Optimize for resolved, role-operable context. Use checkpoint, provisional, and final compile modes honestly.

## Context Compile

Generated context is the best-understood current project overlay. It should not include Charter process history, compile status, role manuals, route tables, model-selection mechanics, or links to workflow-local files.

Use scope or exception notes only when needed to prevent misuse. Keep durable context to decisions, not debate history.

Final compile requires:

- all gates complete
- no weak or unresolved Charter questions
- contradiction pass complete
- `ORCHESTRATOR_CONTEXT.md`, `CREW_CONTEXT.md`, and `GLOSSARY.md` updated
- `.agent-work/CHARTER_OPEN_QUESTIONS.md` absent
- checklist retained for human traceability

## Resources

Use `templates/CHARTER_CHECKLIST.template.md`, `templates/CHARTER_OPEN_QUESTIONS.template.md`, `references/rigorous-default.md`, `references/engineering-rubric.md`, `references/interrogation-protocol.md`, and `references/scenario-bank.md`.
