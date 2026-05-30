# Skill Index

## Constellation Charter
Path: `skills/charter/SKILL.md`

Interrogates engineering doctrine and compiles `ORCHESTRATOR_CONTEXT.md`, `CREW_CONTEXT.md`, `GLOSSARY.md`, and `engine-config.json`.

## Constellation Commander
Path: `skills/commander/SKILL.md`

Runs one bounded issue end to end as the human's rigor scaffold. Owns and drives three checklists (spine, interrogation, execute plan) and dispatches implementer and reviewer subagents per gate.

## Constellation Workbench
Path: `skills/workbench/SKILL.md`

Manages `.agent-work/<work-id>/` and drives the checklist engine (gated/survey).

## Constellation Interrogator
Path: `skills/interrogator/SKILL.md`

Runs a question survey (`interrogation.json`) and consolidates a resolved understanding.

## Constellation Cartographer
Path: `skills/cartographer/SKILL.md`

Maintains the current-only structural map in `docs/architecture/` with sparse purpose/constraint overlays.

## Constellation Scout
Path: `skills/scout/SKILL.md`

Runs map-first architecture audits for bad patterns, inefficient boundaries, and improvement candidates.

## Constellation Implementer
Path: `skills/implementer/SKILL.md`

Implements a bounded change from a handoff, driving its own gated plan.

## Constellation Reviewer
Path: `skills/reviewer/SKILL.md`

Independently verifies a bounded change as a survey and consolidates a verdict.

## Constellation Triage
Path: `skills/triage/SKILL.md`

Classifies and writes issue-ready recommendations for future work. No checklist — works through candidates directly.
