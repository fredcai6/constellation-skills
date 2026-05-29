---
name: constellation-pilot
description: Execute a frozen gate plan gate by gate. Use when handed an execute plan to drive to closure with evidence.
---

# Constellation Pilot

Execute a frozen gate plan, one gate at a time, to closure with integrated evidence.

Drive `execute.json` as a `gated` checklist through the absolute path to this installed skill's bundled engine (`scripts/checklist_engine.py`, workbench `references/checklist-engine.md`). For each gate:

- hand a `CREW_HANDOFF` to a subagent that invokes `constellation-implementer`; integrate its evidence.
- hand the diff and the gate's review criteria to a subagent that invokes `constellation-reviewer`; integrate its verdict.
- close the gate when its postconditions pass.

The gate is the central unit: the smallest chunk, implemented, reviewed, proven with evidence, closable on its own. Pick implementer and reviewer strength from gate complexity, scope, ambiguity, and risk.

Keep the gate list as given. Raise a blocker if a gate is unachievable. Flag out-of-scope finds as triage candidates. When a gate needs current structural truth, request it from a subagent that invokes `constellation-cartographer`.

Templates: `templates/EXECUTE_PLAN.template.json`, `templates/CREW_HANDOFF.template.md`. Reference: workbench `references/checklist-engine.md`.
