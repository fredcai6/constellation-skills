---
name: constellation-charter
description: Interrogate engineering doctrine and compile Orchestrator, Crew, and Glossary context. Use when starting or refreshing repo agent context, posture, standards, or terminology.
---

# Constellation Charter

Elicit engineering doctrine and compile role-operable context.

Durable outputs:

```text
docs/agents/ORCHESTRATOR_CONTEXT.md
docs/agents/CREW_CONTEXT.md
docs/agents/GLOSSARY.md
docs/agents/engine-config.json
.agent-work/templates/*.template.md
```

Workflow outputs:

```text
.agent-work/<work-id>/charter.json
.agent-work/CHARTER_OPEN_QUESTIONS.md
.agent-work/archive/<date>-<work-id>/
```

`CHARTER_OPEN_QUESTIONS.md` exists only while weak or unresolved Charter questions remain. Delete it during final compile.

## Use

Use when starting a repo, refreshing agent context, defining posture, clarifying standards, or naming terms.

Do not use Charter to map architecture, plan features, review diffs, edit code/tests, create issues, or edit non-agent docs.

## Required Context

Read fixed context: `references/rigorous-default.md`, `references/engineering-rubric.md`.

Read target project context when present: `docs/agents/*`, `AGENTS.md`, README/equivalent overview, philosophy/process docs, and user-provided positive exemplars. Inspect code/tests/configs only when a context decision needs light verification. Do not map the codebase.

## Boundaries

Charter informs Orchestrator context for Pilot/Cartographer and Crew context for implementer/reviewer behavior. Do not redesign Constellation topology. If roles fit poorly, stop using these skills.

Allowed writes are the durable and workflow outputs above; all other writes are out of Charter scope.

## Workflow Driver

Before Gate 0, create/resume a `gated` charter checklist (`.agent-work/<work-id>/charter.json`) via the engine. Choose a date-purpose work id unless supplied.

Use `charter.json` as the only Charter todo/decision record; no separate decisions file. It tracks allowed writes, project template catalog, material decision scale, gate order, contradiction pass, role projection, compile checks, and closeout.

Charter seeds and updates project templates. If `.agent-work/templates` is missing, copy bundled defaults there. When decisions change workflow interfaces, update matching project templates too.

Invoke the `constellation-interrogator` skill for Charter interrogation. Start from `templates/CHARTER_STARTING_QUESTIONS.template.md`; aggressively update it. Ask one decision question at a time and continue drilling until the decision is role-operable.

Use `references/rigorous-default.md`, `references/engineering-rubric.md`, `references/interrogation-protocol.md`, and `references/scenario-bank.md` as doctrine/detail sources.

## Context Compile

Generated context is the best-understood current project overlay. It should not include Charter process history, compile status, role manuals, route tables, model-selection mechanics, or links to workflow-local files.

Project shared rules may appear in both contexts, but must use role-specific wording. Orchestrator phrasing explains planning, framing, gating, authority, evidence, or stop/ask impact. Crew phrasing explains implementation, verification, review/blocking, or stop/report impact.

Optimize for context density: minimize tokens, maximize information per token, and sacrifice grammar when meaning stays clear. Keep durable context to decisions, not debate.

Final compile requires the checklist to prove all gates complete, no weak/unresolved Charter questions, contradiction pass complete, durable outputs updated, `.agent-work/CHARTER_OPEN_QUESTIONS.md` absent, and the complete `.agent-work/<work-id>/` package archived.

## Resources

Templates: `templates/ENGINE_CONFIG.template.json`, `templates/CHARTER_OPEN_QUESTIONS.template.md`, `templates/ORCHESTRATOR_CONTEXT.template.md`, `templates/CREW_CONTEXT.template.md`, `templates/GLOSSARY.template.md`.

References: `references/rigorous-default.md`, `references/engineering-rubric.md`, `references/interrogation-protocol.md`, `references/scenario-bank.md`.
