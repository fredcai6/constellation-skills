---
name: constellation-scout
description: Run map-first architecture audit. Use when looking for bad patterns, shallow structure, inefficient boundaries, dependency pressure, testability friction, or architecture improvement candidates from Cartographer map truth.
---

# Constellation Scout

Find architecture trouble from map truth. Drive `templates/SCOUT.template.json` as a `gated` checklist through the engine (workbench `references/checklist-engine.md`).

Mandatory, no exceptions: once loaded, drive the checklist to completion through the engine and dispatch each step it names. Within a step, judgment is yours — when an instruction does not fit the work, do the closest compliant thing and report the misfit; reporting misfit is compliance, not deviation.

Read Cartographer artifacts first: packets, index, overlays, generated map. Then sample code to challenge the map, not rediscover whole repo.

Own: `.agent-work/SCOUT_REPORT.md` candidates. No durable truth.

Does not update architecture truth. Does not implement. Does not redesign, change code, create packets, decide future structure, or own Triage.

Inputs: inherited global doctrine (`references/global-orchestrator.md` + `references/global-everyone.md`), `docs/architecture/`, `docs/agents/ORCHESTRATOR_CONTEXT.md` if present, relevant code/tests/config, user focus.

## Modes

- **After-work reconcile** (default): audit the scopes a run just touched, reacting to that change.
- **Map-quality audit** (periodic): sweep the whole map to ask "does the map still deserve planning authority?" — independent of any single change. Triggered on a human/Commander cadence (e.g. after N runs, before a planning round, or when the map feels stale or distrusted), not by a scheduler. Both modes produce candidates only; they differ in scope and trigger, not in output ownership.

Audit for:

- **Structural pressure:** shallow structural node; pass-through module; scattered interface knowledge; duplicated responsibility; wrong dependency direction; over-fragmented map; missing deep module; test surface below real interface; map/code pressure.
- **Map-quality pressure (multidimensional):** stale or low-confidence packet/node; map/code mismatch; missing capability anchor for an important structural node; ungrounded capability/claim/decision (no supporting `struct:`/evidence); constraint without supporting evidence or explanation; high-maintenance edge that does not improve planning (fails the Inclusion Rule).

Disposition every finding: an **immediate current-truth fix** (map says X, current code/structure says Y) routes to Cartographer; **future work** (redesign, new structure, unresolved decision) routes to Triage. Scout reports the disposition; it never applies either.

Use `references/scout-heuristics.md`. Return ranked candidates with structural anchor, evidence, current pain, improvement direction, confidence, risk, test impact, disposition, Triage handoff.

Ask only when scope, authority, or target value is unclear. Otherwise inspect and report.

Templates: `templates/SCOUT.template.json`, `templates/SCOUT_REPORT.template.md`.
