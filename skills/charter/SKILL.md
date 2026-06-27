---
name: constellation-charter
description: Interrogate engineering doctrine and compile Orchestrator, Crew, Glossary, and engine config. Use when starting or refreshing repo agent context, posture, standards, or terminology.
---

# Constellation Charter

Turn a loose project idea into role-operable context: how the project wants problems approached, what rules the crew must follow, and the terms everyone shares.

**Mandatory, no exceptions: once loaded, drive the checklist to completion through the engine and dispatch each step it names. Within a step, judgment is yours — when an instruction does not fit the work, do the closest compliant thing and report the misfit; reporting misfit is compliance, not deviation.**

Drive `templates/CHARTER.template.json` as a `gated` checklist through the absolute path to this installed skill's bundled engine (`scripts/checklist_engine.py`, workbench `references/checklist-engine.md`): capture intent, explore existing code, interrogate doctrine, set the rigor level and prune confirmation gates to it, write each durable document as its own gate confirmed by the user, seed project templates, compile.

Durable outputs:

```text
docs/agents/ORCHESTRATOR_CONTEXT.md   # project deltas over inherited global-orchestrator doctrine
docs/agents/CREW_CONTEXT.md           # project deltas over inherited global-crew doctrine
docs/agents/GLOSSARY.md               # shared terms only
docs/agents/AGENT_GUIDE.md            # single repo-orientation guide (TOC, repo layout, doc map); the shared middle of the two contexts
AGENTS.md, CLAUDE.md                  # root pointer files that redirect to docs/agents/AGENT_GUIDE.md
docs/agents/engine-config.json        # rework cap, rigor checkpoints, rules root, repo guidance
.agent-work/templates/*               # project-specific template versions
```

## Compile

The global approach baseline is **inherited, not authored here**: roles load `references/global-orchestrator.md` / `references/global-crew.md` / `references/global-everyone.md` (bundled with each skill at install) at their context-read step. Charter writes only the **project deltas** over that baseline — never restate inherited doctrine. ORCHESTRATOR deltas cover project facts (purpose, authority), non-default rigor, and planning/evidence/stop-ask departures; CREW deltas cover project rules that change implementation or review. Optimize for density: minimize tokens, maximize information per token, sacrifice grammar when meaning stays clear. Keep durable context to decisions, free of process history.

**FOLLOW THIS SKILL STRICTLY. USE THE ENGINE RIGOROUSLY**

Templates: `templates/CHARTER.template.json`, `templates/CHARTER_STARTING_QUESTIONS.template.md`, `templates/ENGINE_CONFIG.template.json`, `templates/ORCHESTRATOR_CONTEXT.template.md`, `templates/CREW_CONTEXT.template.md`, `templates/GLOSSARY.template.md`, `templates/AGENT_GUIDE.template.md`, `templates/AGENTS.pointer.template.md`, `templates/CLAUDE.pointer.template.md`, `templates/CHARTER_OPEN_QUESTIONS.template.md`. References: `references/rigorous-default.md`, `references/engineering-rubric.md`, `references/interrogation-protocol.md`, `references/scenario-bank.md`.
