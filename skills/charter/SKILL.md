---
name: constellation-charter
description: Interrogate engineering doctrine and compile Orchestrator, Crew, and Glossary context. Use when starting or refreshing repo agent context, posture, standards, or terminology.
---

# Constellation Charter

## Purpose

Elicit engineering doctrine and compile role-operable context.

Durable outputs:

```text
docs/agents/ORCHESTRATOR_CONTEXT.md
docs/agents/CREW_CONTEXT.md
docs/agents/GLOSSARY.md
.agent_work/templates/*.template.md
```

Workflow outputs:

```text
.agent-work/<work-id>/CHARTER_CHECKLIST.md
.agent-work/CHARTER_OPEN_QUESTIONS.md
.agent-work/archive/<date>-<work-id>/
```

`CHARTER_OPEN_QUESTIONS.md` exists only while weak or unresolved Charter questions remain. Delete it during final compile.

## Use

Use when starting a repo, refreshing agent context, defining posture, clarifying standards, or naming terms.

Do not use Charter to map architecture, plan features, review diffs, edit code/tests, create issues, or edit non-agent docs.

## Required Context

Fixed context:

```text
docs/CONSTELLATION_OVERVIEW.md
docs/OPERATING_PRINCIPLES.md
skills/pilot/SKILL.md
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

Inspect code/tests/configs only when a context decision needs light verification. Do not map the codebase.

## Fixed Boundaries

Charter informs Orchestrator context for Pilot/Cartographer and Crew context for implementer/reviewer behavior.

Do not redesign Constellation topology. If roles fit poorly, stop using these skills.

Allowed writes:

```text
.agent-work/<work-id>/CHARTER_CHECKLIST.md
.agent-work/CHARTER_OPEN_QUESTIONS.md
.agent-work/archive/<date>-<work-id>/
docs/agents/ORCHESTRATOR_CONTEXT.md
docs/agents/CREW_CONTEXT.md
docs/agents/GLOSSARY.md
.agent_work/templates/*.template.md
```

All other writes are out of Charter scope.

## Workflow Driver

Before Gate 0, create/resume `.agent-work/<work-id>/CHARTER_CHECKLIST.md`. Prefer `.agent_work/templates/CHARTER_CHECKLIST.template.md`; fall back to bundled `templates/CHARTER_CHECKLIST.template.md`. Choose a date-purpose work id unless supplied.

Charter seeds/updates project templates. If `.agent_work/templates` is missing, copy bundled defaults there. When decisions change workflow interfaces, update matching project templates too.

The checklist is the only Charter todo/decision record; no separate decisions file.

Invoke `constellation-interrogator` for Charter interrogation. Start from `templates/CHARTER_STARTING_QUESTIONS.template.md`; aggressively update it. Ask one decision question at a time. Gate 0 may collect exemplars and repo action authority.

## Interrogation Rules

Start from `references/rigorous-default.md`. User may accept, relax, or strengthen it by subsystem; rigor is not opt-in.

Use `references/engineering-rubric.md` for required axes. Touch every axis. Mark `not-material` only with user agreement.

A material decision affects future agent behavior, allowed scope, evidence requirements, failure behavior, interfaces/contracts, canonical inputs, documentation duties, dependency policy, security/privacy/publicness, performance/resource posture, generated artifacts, compromise policy, or stop/report conditions.

For each material decision, state:

```text
Default -> Cost -> Relaxation -> Scenario -> Decision -> Evidence
```

Do not accept slogans like "do it right", "be careful", "use judgment", "write tests", "move fast", or "reasonable defaults". Convert them into cost, scenario, evidence, and role implication.

Record material decisions in the checklist with:

```text
Quality: strong | usable | weak | unresolved | not-material
Authority: user decision | accepted default | unconfirmed default | repo artifact | assumption
Posture: rigorous-default | relaxed | strengthened | mixed | not-applicable
Projection: orchestrator | crew | both | glossary | checklist-only
Projection reason: planning/framing | gating/evidence | authority/scope | implementation | verification | review/blocking | stop/report | terminology | local traceability
```

Every material decision needs role-use projection. Shared project invariants default to `both` unless role-specific. Architecture and scope policy is usually Orchestrator-only; Crew receives consequences through the handoff.

Weak/unresolved decisions remain visible in `.agent-work/CHARTER_OPEN_QUESTIONS.md` during provisional compile.

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

Project shared rules may appear in both contexts, but must be role-specific wording. Orchestrator phrasing explains planning, framing, gating, authority, evidence, or stop/ask impact. Crew phrasing explains implementation, verification, review/blocking, or stop/report impact.

Crew context contains only rules consumed within a handoff. Workflow selection and coordination consequences reach Crew through the handoff.

Use scope/exception notes only when needed to prevent misuse. Keep durable context to decisions, not debate.

Final compile requires:

- all gates complete
- no weak or unresolved Charter questions
- contradiction pass complete
- `ORCHESTRATOR_CONTEXT.md`, `CREW_CONTEXT.md`, and `GLOSSARY.md` updated
- `.agent-work/CHARTER_OPEN_QUESTIONS.md` absent
- move the entire `.agent-work/<work-id>/` package to archive, including `INTERROGATOR_QUESTIONS.md`

## Resources

Use `templates/CHARTER_CHECKLIST.template.md`, `templates/CHARTER_OPEN_QUESTIONS.template.md`, `references/rigorous-default.md`, `references/engineering-rubric.md`, `references/interrogation-protocol.md`, and `references/scenario-bank.md`.
