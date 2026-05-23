---
name: constellation-charter
description: Elicit project ground rules through relentless scenario-based interrogation and compile standalone agent context documents. Use when starting or refreshing repo agent rules, philosophy, standards, or docs/agents context.
---

# Constellation Charter

## Purpose

Initialize or refresh project ground rules that align Constellation agents with the user.

Outputs: `docs/agents/ORCHESTRATOR_CONTEXT.md`, `IMPLEMENTER_REVIEWER_CONTEXT.md`, `OPEN_QUESTIONS.md`, and `GLOSSARY.md`.

## Use

Use when starting a project, preparing an unmanaged repo before Cartographer work, or defining ground rules, agent context, project philosophy, or coding/review standards.

Do not use to map code, plan a feature, review a diff, update architecture after implementation, or write code.

## Required Context

Before asking project-specific questions, read:

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

Treat that as the fixed delegation model. Do not re-ask whether Conductor, Cartographer, Crew, Workbench, or Triage should exist unless the user explicitly wants to customize Constellation.

Ask how those skills should behave in this repo: autonomy limits, evidence standards, issue creation authority, tooling assumptions, escalation thresholds, and project-specific defaults.

Also inspect `docs/agents/`, `AGENTS.md`, philosophy docs, architecture docs, and process docs. Assume existing artifacts are true unless the user says they are stale, incomplete, experimental, or should be replaced. When refreshing context, preserve prior decisions unless changed; do not replace context wholesale without showing what changed.

## Interrogation Contract

Charter is a relentless interrogation pass, not a setup wizard.

Ask one question at a time. Each question must pursue a decision, not complete a questionnaire.

Assume the first answer to an important question is too shallow. Continue drilling until the answer names:

- concrete use case
- actor or subsystem
- output or behavior
- input/source of truth
- failure consequence
- evidence expectation
- agent action implication

Do not accept slogans such as "move fast", "be careful", "use tests", "ask when unsure", "agents can decide", or "reasonable defaults". Convert them into project-specific behavior with a scenario.

If the user gives a vague answer, ask a narrower follow-up. If the user says "I don't care", select a visible default and test it with a scenario. If the user says to stop, stop and produce a checkpoint.

## Opening Sequence

Drill project reality before agent autonomy:

1. What the project does.
2. Who or what uses the outputs.
3. What actions or decisions the outputs influence.
4. What the canonical inputs/data/source-of-truth are.
5. What failure looks like: wrong, stale, missing, slow, misleading, unreproducible, or overconfident.
6. What evidence would prove the project is working.
7. What parts are research/prototype versus durable system behavior.
8. What existing docs, tests, and commands agents should treat as current authority.

Only after this baseline should Charter ask about Conductor, Cartographer, Crew, Workbench, and Triage behavior.

## Scenario Pattern

For each important area, force at least one concrete scenario:

```text
When <specific situation> happens, should the agent do A, B, or C?
What would be unacceptable?
What evidence would prove the agent handled it correctly?
Who owns the decision if the tradeoff is real?
```

Use `references/interrogation-protocol.md` for the follow-up ladder, shallow-answer triggers, resistance handling, and completion test. Use `references/scenario-bank.md` for seed scenarios; adapt them to the user's project instead of reading them verbatim.

## Checkpoints And Compile

Periodically summarize:

- settled decisions
- weak answers that need another pass
- contradictions
- defaults selected because the user did not care
- open questions
- areas not yet interrogated

Use summaries to continue drilling, not to finish early. Do not optimize for one-session completion.

Compile final docs only when the user asks to compile, says to use defaults for the rest, or the completion test passes. Before compiling, run a contradiction pass.

## Context Curation

Charter curation keeps `docs/agents/` lean after rule elicitation. Edit generated context directly for clarity; ask before deleting unique policy, changing authority/evidence/failure meaning, or resolving an open question.

## Default policy library

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

## Required Areas

Cover project purpose/users, output authority/failure cost, repo/tooling, ambiguity, scope/refactoring, architecture/ownership, contracts, compatibility, errors/degraded modes, reporting/audit, validation, side effects, testing/evidence, data truth, docs, dependencies, security/privacy, performance, generated artifacts, and autonomy.

Do not mark an area complete until it has project-specific examples and at least one agent-action implication.

## Resources

Use `templates/`, `references/scenario-bank.md`, and `references/interrogation-protocol.md`.
