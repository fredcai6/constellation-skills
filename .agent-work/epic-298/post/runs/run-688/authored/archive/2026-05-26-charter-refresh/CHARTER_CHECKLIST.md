# Charter Checklist: F1Brainz Charter Refresh

This file records the 2026-05-26 Charter completion audit after the Charter skill added project template catalog and archive closeout requirements.

## Allowed Writes

```text
.agent-work/2026-05-26-charter-refresh/CHARTER_CHECKLIST.md
.agent-work/2026-05-26-charter-refresh/INTERROGATOR_QUESTIONS.md
.agent-work/CHARTER_OPEN_QUESTIONS.md
.agent-work/archive/2026-05-26-charter-refresh/
docs/agents/ORCHESTRATOR_CONTEXT.md
docs/agents/CREW_CONTEXT.md
docs/agents/GLOSSARY.md
.agent-work/templates/*.template.md
```

All other writes are out of Charter scope.

## Project Template Catalog

Charter seeds and updates project templates.

**Lookup rule:** prefer `.agent-work/templates/<template-name>`; fall back to bundled `templates/<template-name>`.
**Seed status:** updated this run.
**Template changes needed:** none; bundled defaults match the updated Charter skill contract and no project-specific workflow interface change was identified.
**Template update evidence:** `.agent-work/templates/CHARTER_CHECKLIST.template.md`, `.agent-work/templates/CHARTER_OPEN_QUESTIONS.template.md`, `.agent-work/templates/ORCHESTRATOR_CONTEXT.template.md`, `.agent-work/templates/CREW_CONTEXT.template.md`, `.agent-work/templates/GLOSSARY.template.md`.
**Closeout feedback:** none provided.

## Run State

**Work ID:** `2026-05-26-charter-refresh`
**Charter scope:** whole repo refresh; completion audit only.
**Compile mode:** final.
**Current gate:** Gate 6 (Closeout).
**Current next question:** n/a.
**Why this question matters:** n/a.
**Recommendation/default:** n/a.
**Waiting on user:** no.

## Repo Action Authority

**Commit sensitivity:** commit local ok; push/PR ask first.
**Pilot may open PRs directly:** ask first.
**Pilot may merge to main:** ask first.
**Commit archived work packages:** no explicit project rule; leave uncommitted unless human requests.
**Archived package commit decision:** accepted from current durable contexts: push/PR/merge require asking, local edits are autonomous.

## Gate 0: Bootstrap - COMPLETE

- Existing durable contexts present: `docs/agents/ORCHESTRATOR_CONTEXT.md`, `docs/agents/CREW_CONTEXT.md`, `docs/agents/GLOSSARY.md`.
- Project overview and doc map checked: `README.md`, `docs/DOCUMENTATION.md`, `docs/architecture/index.md`, `docs/AGENT_GUIDE.md`.
- `.agent-work/templates` was missing and seeded from the bundled Charter templates.
- Required fixed context paths named by the skill (`docs/CONSTELLATION_OVERVIEW.md`, `docs/OPERATING_PRINCIPLES.md`, `skills/pilot/SKILL.md`, `skills/cartographer/SKILL.md`, `skills/crew/SKILL.md`) were not present in this installed skill tree. Available role skill files were read instead: `constellation-pilot`, `constellation-cartographer`, `constellation-crew`.

## Gate 1: Operating Context - COMPLETE

No durable context change required. Existing context still matches current repo docs:

- F1 race prediction and fantasy strategy tool.
- SQLite DB is canonical for all analysis.
- Promoted predictions/reports/manifests have correctness and reproducibility implications.
- Subsystem rigor profiles remain data layer, physics, evo, and exploratory.

## Gate 2: Engineering Rubric - COMPLETE

No new material doctrine decisions found. Existing decisions still cover:

- DB-only analysis.
- Strict input validation and clear failures.
- Test-led implementation for logic changes.
- Full region verification.
- Generated artifact policy.
- Explicit issue-backed compromise tracking.

## Gate 3: Implementation Conventions - COMPLETE

No durable context change required. Existing conventions still match current AGENTS/project-doc instructions:

- Use `py`, not `python`.
- Use `py -m pytest tests/...`.
- Keep function inputs strict and interfaces documented.
- Prefer fail-fast behavior with clear failure modes.
- Update docs alongside code.

## Gate 4: Contradiction Pass - COMPLETE

- No live durable-context contradiction found.
- Prior checklist references deleted legacy docs (`docs/PROJECT_PHILOSOPHY.md`, `docs/ARCHITECTURE.md`, `CLAUDE.md`), but those references are historical workflow trace only and are not projected into durable context.
- Current documentation map correctly points to `docs/architecture/index.md`.

## Gate 5: Context Compile - COMPLETE

No rewrite needed:

- `docs/agents/ORCHESTRATOR_CONTEXT.md` contains planning, evidence, authority, canonical data, architecture boundary, docs, compromise, and stop/ask rules.
- `docs/agents/CREW_CONTEXT.md` contains implementation, verification, DB-only, interface, failure, docs, generated artifact, review blocker, and stop/report rules.
- `docs/agents/GLOSSARY.md` contains current shared repo terms.
- Project templates are now present for future Charter runs.

## Gate 6: Closeout - COMPLETE

- [x] All gates complete.
- [x] No `weak` or `unresolved` material decisions remain.
- [x] Contradiction pass complete.
- [x] `docs/agents/ORCHESTRATOR_CONTEXT.md` checked.
- [x] `docs/agents/CREW_CONTEXT.md` checked.
- [x] `docs/agents/GLOSSARY.md` checked.
- [x] `.agent-work/templates` seeded and project-specific template changes applied or explicitly skipped.
- [x] Template update candidates consumed, routed to Charter decisions, or dropped because none were present.
- [x] Shared project invariants default to `both` unless clearly role-specific.
- [x] Crew context contains every project invariant found in this audit that can change implementation, verification, review/blocking, or stop/report behavior.
- [x] Orchestrator context contains every project invariant found in this audit that changes framing, gate design, authority/scope decisions, evidence selection, or stop/ask behavior.
- [x] Crew context contains only universal verification rules; area-specific commands are represented as handoff requirements.
- [x] Handoff-only details are not placed in durable Crew context.
- [x] `.agent-work/CHARTER_OPEN_QUESTIONS.md` absent.
- [x] Move the entire `.agent-work/2026-05-26-charter-refresh/` package to `.agent-work/archive/2026-05-26-charter-refresh/`, including `INTERROGATOR_QUESTIONS.md`.
- [x] No loose Charter work-id artifacts remain.

## Material Decisions

| ID | Gate | Decision | Quality | Authority | Posture | Projection | Projection reason |
|---|---|---|---|---|---|---|---|
| D-001 | 0 | Seed project Charter templates from updated bundled defaults | strong | repo artifact | rigorous-default | checklist-only | local traceability |
| D-002 | 5 | Durable agent context remains current; no rewrite required | strong | repo artifact | rigorous-default | checklist-only | local traceability |

## Contradiction Register

| ID | Conflict | Status | Resolution |
|---|---|---|---|
| C-001 | Historical checklist references deleted docs that no longer exist | resolved | Do not project historical references; current durable context and documentation map are authoritative for future runs. |

## Compile History

| Date | Mode | Outputs touched | Remaining weak/unresolved |
|---|---|---|---|
| 2026-05-26 | final | `.agent-work/templates/*.template.md`, refresh checklist | none |
