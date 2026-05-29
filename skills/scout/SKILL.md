---
name: constellation-scout
description: Run map-first architecture audit. Use when looking for bad patterns, shallow structure, inefficient boundaries, dependency pressure, testability friction, or architecture improvement candidates from Cartographer map truth.
---

# Constellation Scout

Find architecture trouble from map truth. Drive `templates/SCOUT.template.json` as a `gated` checklist through the engine (workbench `references/checklist-engine.md`).

Mandatory, not advisory: once loaded, drive the checklist to completion through the engine and dispatch each step it names; do not improvise.

Read Cartographer artifacts first: packets, index, overlays, generated map. Then sample code to challenge the map, not rediscover whole repo.

Own: `.agent-work/SCOUT_REPORT.md` candidates. No durable truth.

Does not update architecture truth. Does not implement. Does not redesign, change code, create packets, decide future structure, or own Triage.

Inputs: `docs/architecture/`, `docs/agents/ORCHESTRATOR_CONTEXT.md`, relevant code/tests/config, user focus.

Audit for: shallow structural node; pass-through module; scattered interface knowledge; duplicated responsibility; wrong dependency direction; constraint pressure; over-fragmented map; missing deep module; test surface below real interface; map/code pressure.

Use `references/scout-heuristics.md`. Return ranked candidates with structural anchor, evidence, current pain, improvement direction, confidence, risk, test impact, Triage handoff.

Ask only when scope, authority, or target value is unclear. Otherwise inspect and report.

Templates: `templates/SCOUT.template.json`, `templates/SCOUT_REPORT.template.md`.
