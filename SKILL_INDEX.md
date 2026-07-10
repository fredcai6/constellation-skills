# Skill Index

## Constellation Charter
Path: `skills/charter/SKILL.md`

Interrogates engineering doctrine and compiles project-delta `ORCHESTRATOR_CONTEXT.md` / `CREW_CONTEXT.md` (over the inherited global doctrine bundled with each skill), `GLOSSARY.md`, and `engine-config.json`.

## Constellation Commander
Path: `skills/commander/SKILL.md`

Runs one bounded issue end to end as the human's rigor scaffold. Owns and drives three checklists (spine, interrogation, execute plan) and dispatches implementer and reviewer subagents per gate.

## Constellation Commander (delegated)
Path: `skills/commander-delegated/SKILL.md`

Runs one bounded issue end to end under a frozen Admiral LAUNCH_ORDER, autonomously — the delegated entry over the same commander core doctrine and templates as `constellation-commander`.

## Constellation Explorer
Path: `skills/explorer/SKILL.md`

Shapes a raw idea into a human-confirmed, issue-ready design upstream of any issue: exploration cycles, excursion off/on-ramps, a cold critic panel, and a hard confirmation gate before work is cut.

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

## Constellation Docent
Path: `skills/docent/SKILL.md`

Generates a self-contained, stamped static HTML explainer site from Cartographer map truth so a human can browse the architecture; a read-only map consumer that flags itself stale when the map moves.

## Constellation Implementer
Path: `skills/implementer/SKILL.md`

Implements a bounded change from a handoff, driving its own gated plan.

## Constellation Reviewer
Path: `skills/reviewer/SKILL.md`

Independently verifies a bounded change as a survey and consolidates a verdict.

## Constellation Prototyper
Path: `skills/prototyper/SKILL.md`

Builds a throwaway prototype that answers one named design question, then disposes of it. Handoff-driven, no checklist.

## Constellation Triage
Path: `skills/triage/SKILL.md`

Classifies and writes issue-ready recommendations for future work. No checklist — works through candidates directly.

## Constellation Admiral
Path: `skills/admiral/SKILL.md`

Runs an epic as the human's delegate: confirms a latitude contract, dispatches Commanders in waves, adjudicates and merges, and closes with lessons and architecture audits.

## Constellation Lessons Auditor
Path: `skills/lessons-auditor/SKILL.md`

Fresh-context Reflector dispatched at closeout: distills scoped, grounded lesson candidates from run artifacts and routes them as nominations, never applying them itself.

## Constellation Curator
Path: `skills/curator/SKILL.md`

Runs a mechanical measurement pass over the skill corpus (`curate_corpus.py`) and turns the findings into scoped, grounded consolidation candidates — a solo, human-invoked role that dispatches no crew and drives no engine checklist.
