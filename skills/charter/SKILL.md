---
name: constellation-charter
description: Interrogate engineering doctrine and compile Orchestrator, Crew, Glossary, and engine config. Use when starting or refreshing repo agent context, posture, standards, or terminology.
---

# Constellation Charter

Turn a loose project idea into role-operable context: how the project wants problems approached, what rules the crew must follow, and the terms everyone shares.

Mandatory, not advisory: once loaded, drive the checklist to completion through the engine and dispatch each step it names; do not improvise.

Drive `templates/CHARTER.template.json` as a `gated` checklist through the engine (`scripts/checklist_engine.py`, workbench `references/checklist-engine.md`): capture intent, explore existing code, interrogate doctrine, set the rigor level and prune confirmation gates to it, write each durable document as its own gate confirmed by the user, seed project templates, compile.

Durable outputs:

```text
docs/agents/ORCHESTRATOR_CONTEXT.md   # planning, authority, gating, evidence, stop/ask
docs/agents/CREW_CONTEXT.md           # implementation, verification, review/blocking, stop/report
docs/agents/GLOSSARY.md               # shared terms only
docs/agents/engine-config.json        # rework cap, rigor checkpoints, rules root, repo guidance
.agent-work/templates/*               # project-specific template versions
```

## Interrogate as a subagent

Synthesize what is known into a handoff and pass it, with `templates/CHARTER_STARTING_QUESTIONS.template.md`, to a subagent that invokes `constellation-interrogator`. It resolves the doctrine and returns the understanding; integrate that. At each document gate, confirm the context with the user and capture any special rules.

## Compile

Write each context for its reader: ORCHESTRATOR phrasing explains planning, framing, gating, authority, evidence, stop/ask impact; CREW phrasing explains implementation, verification, review/blocking, stop/report impact. A shared rule may appear in both, in role-specific wording. Optimize for density: minimize tokens, maximize information per token, sacrifice grammar when meaning stays clear. Keep durable context to decisions, free of process history.

## Boundaries

Charter compiles context; it does not map architecture, plan features, review diffs, edit code, or redesign Constellation topology. If the roles fit poorly, stop using these skills.

Templates: `templates/CHARTER.template.json`, `templates/CHARTER_STARTING_QUESTIONS.template.md`, `templates/ENGINE_CONFIG.template.json`, `templates/ORCHESTRATOR_CONTEXT.template.md`, `templates/CREW_CONTEXT.template.md`, `templates/GLOSSARY.template.md`, `templates/CHARTER_OPEN_QUESTIONS.template.md`. References: `references/rigorous-default.md`, `references/engineering-rubric.md`, `references/interrogation-protocol.md`, `references/scenario-bank.md`.
