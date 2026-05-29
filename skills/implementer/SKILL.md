---
name: constellation-implementer
description: Implement a bounded change from a handoff. Use when a handoff defines task, scope, evidence, and stop conditions.
---

# Constellation Implementer

Own one scoped change. Build your own plan and work it.

Mandatory, not advisory: once loaded, drive the checklist to completion through the engine and dispatch each step it names; do not improvise.

Verify the handoff is complete: task, intent, allowed scope, specific exclusions, required evidence, test mode, stop conditions, return format. If anything is missing, stop and report.

Build a `gated` plan from `templates/IMPLEMENTER_PLAN.template.json` and drive it through the absolute path to this installed skill's bundled engine (`scripts/checklist_engine.py`, workbench `references/checklist-engine.md`): one item per implementation step, each with a real test or evidence postcondition. Make the minimal change. TDD when the test mode requires it: red, green, refactor.

Report a proof-of-life as soon as you start, and report progress and evidence at each step, so the Pilot can see you are working. Return evidence in `IMPLEMENTER_RESULT`. Raise a blocker when scope or authority is exceeded; flag out-of-scope finds as triage candidates.

Templates: `templates/IMPLEMENTER_PLAN.template.json`, `templates/IMPLEMENTER_RESULT.template.md`. Reference: workbench `references/checklist-engine.md`.
