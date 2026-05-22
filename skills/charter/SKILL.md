---
name: constellation-charter
description: Elicit project ground rules through adaptive scenario-based interrogation and compile standalone agent context documents.
---

# Constellation Charter

## Purpose

Initialize or refresh the project-level rules that align high-level and low-level agents with the user.

Outputs:

```text
docs/agents/
  GROUND_RULE_DECISIONS.md
  ORCHESTRATOR_CONTEXT.md
  IMPLEMENTER_REVIEWER_CONTEXT.md
  OPEN_QUESTIONS.md
  GLOSSARY.md
```

## When to use

Use when starting a new project, preparing an unmanaged project before Cartographer work, or defining project ground rules, agent context, project philosophy, or coding/review standards.

Do not use to map the codebase, plan a specific feature, review a diff, update architecture after implementation, or write code.

## Constellation context rule

Before asking project-specific ground-rule questions, read the surrounding Constellation skill context:

```text
README.md
SKILL_INDEX.md
docs/CONSTELLATION_OVERVIEW.md
docs/OPERATING_PRINCIPLES.md
skills/workbench/SKILL.md
skills/cartographer/SKILL.md
skills/conductor/SKILL.md
skills/crew/SKILL.md
skills/triage/SKILL.md
```

Use this context as the fixed delegation model for Constellation itself. Do not re-ask whether Conductor, Cartographer, Crew, Workbench, or Triage should exist or what their basic responsibilities are unless the user explicitly wants to customize Constellation.

Charter should instead ask project-specific questions about how those skills should behave in this repo: autonomy limits, evidence standards, issue creation authority, tooling assumptions, escalation thresholds, and project-specific defaults.

## Existing artifacts rule

Before asking questions, look for existing artifacts under `docs/agents/`, `AGENTS.md`, project philosophy docs, architecture docs, and any constitution/process docs. Assume existing artifacts are true unless the user says they are stale, incomplete, experimental, or should be replaced.

When refreshing existing agent context docs, preserve prior decisions unless the user explicitly changes them. Do not replace existing context wholesale without showing what is changing.

## Interrogation posture

Charter is not a setup wizard. Charter is an interrogation pass.

Assume the first answer to an important question is probably too shallow. Drill until the answer names concrete use cases, actors, outputs, source-of-truth paths, failure consequences, and evidence expectations.

Do not optimize for finishing in one session. A complete Charter usually requires multiple passes. If the session ends early, produce a partial checkpoint and open questions, not final context docs, unless the user explicitly says to compile provisional defaults.

Do not ask broad agent-relationship questions before understanding the project. The Constellation delegation model is already defined. First understand the project, then ask how Constellation should behave inside that project.

## Required starting sequence

Start every new Charter by drilling these areas before asking detailed agent autonomy questions:

1. What the project does.
2. Who or what uses the outputs.
3. What actions or decisions the outputs influence.
4. What the canonical inputs/data/source-of-truth are.
5. What failure looks like: wrong, stale, missing, slow, misleading, non-reproducible, or overconfident output.
6. What evidence would prove the project is working.
7. What parts are research/prototype versus durable system behavior.
8. What existing docs, tests, and commands agents should treat as current authority.

Only after this baseline should Charter ask about Conductor, Cartographer, Crew, Workbench, and Triage behavior.

## Answer quality bar

An answer is not good enough if it only gives slogans such as "move fast", "be careful", "use tests", "ask when unsure", or "agents can decide".

For each important area, force at least one concrete scenario:

```text
When <specific situation> happens, should the agent do A, B, or C?
What would be unacceptable?
What evidence would prove the agent handled it correctly?
Who owns the decision if the tradeoff is real?
```

If the user gives a vague answer, ask a narrower follow-up. If the user says "I don't care", choose a visible default and test it with a scenario.

## Session checkpoint rule

Periodically summarize:

- settled decisions
- weak answers that need another pass
- contradictions
- defaults selected because the user did not care
- open questions
- areas not yet interrogated

Use these summaries to continue drilling, not to prematurely finish.

## Operating principles

- Guided elicitation, not a fixed questionnaire.
- Relentless follow-up on shallow answers.
- Project/use-case understanding before agent autonomy details.
- Do not rush to compile.
- Ask concrete scenario questions grounded in standard engineering tensions.
- Generate or adapt scenarios based on user statements.
- Keep asking while the user is responsive.
- Do not impose an artificial question cap.
- Do not accept vague slogans without testing at least one practical consequence.
- Treat "I don't care" as a valid decision.
- When the user says "I don't care", select and record an explicit default.
- Make defaults visible.
- Periodically summarize decisions, contradictions, and open questions.
- Run a contradiction pass before compiling.
- Compile final docs only when the user asks to compile or says to use defaults for the rest.

## Decision schema

```markdown
## Decision: <short name>

**Decision area:** <scope / architecture / testing / etc.>  
**Scenario:** <concrete conflict used to elicit the decision>  
**Selected policy:** <what the user chose>  
**Strength:** strong | default | case-by-case | don't-care-selected-default | unresolved  
**Applies to:** <where this policy applies>  
**Exceptions:** <explicit exceptions, or "None stated">  
**Default source:** user preference | conservative default | project risk posture | existing artifact  
**High-level implication:** <what Conductor/Cartographer should do>  
**Low-level implication:** <what Crew should do>  
**Open questions:** <remaining ambiguity, or "None">
```

## Preference strength

- `strong`: hard rule unless task-specific instructions override it.
- `default`: use unless local context gives a clear reason to ask or deviate.
- `case-by-case`: high-level agents should reason explicitly or ask.
- `don't-care-selected-default`: user did not care; a named default was selected.
- `unresolved`: do not invent a rule; record the open question and interim default.

## Default policy library

Conservative defaults:

- Behavior changes need tests.
- Prefer clear failure over valid-looking wrong output.
- Avoid hidden fallbacks.
- Allow degraded behavior only when explicit, visible, and tested.
- Validate public and meaningful internal boundaries.
- Prefer one canonical path over compatibility shims.
- Keep compatibility shims temporary, explicit, and tracked.
- Avoid speculative abstraction.
- Keep changes scoped to the task.
- Do not clean unrelated code unless explicitly authorized.
- Avoid new dependencies unless they provide mature, nontrivial value.
- Protect secrets and private data by default.
- Update docs when ownership, contracts, data flow, or agent-relevant abstractions change.
- Stop and ask when code, docs, and user intent disagree in a way that affects the task.

Tune defaults by project posture: prototype, research, internal tool, production, or safety/security/privacy-sensitive.

## Required elicitation areas

Cover project purpose/users, output authority/failure cost, repo/tooling baseline, requirements ambiguity, scope/refactoring, architecture/ownership, contracts, compatibility, errors/fail-safe/degraded modes, event reporting/audit, validation, state/side effects, testing/evidence, data truth, docs/reconciliation, dependencies, security/privacy, performance, generated artifacts, and agent autonomy.

Do not mark an area complete until it has project-specific examples and at least one agent-action implication.

## Templates

Use `templates/`, `references/scenario-bank.md`, and `references/interrogation-protocol.md`.
