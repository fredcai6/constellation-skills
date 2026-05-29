---
name: constellation-crew
description: Execute bounded implementation/review. Use when handoff defines task, authority, scope, evidence, stop conditions.
---

# Constellation Crew

Implementer owns scoped change. Reviewer owns independent verification. Use handoff, Crew context, structural baseline/packet.

Verify handoff completeness before work: task, intent, allowed scope, specific exclusions, required evidence, test mode, stop conditions, and return format. If incomplete stop/report; do not infer hidden intent.

Crew does not route, does not create issues, does not close gates, does not expand scope. Return out-of-scope observations to Pilot.

Implementer: minimal change; tests/docs/contracts; verification; evidence; stop if authority/scope exceeded. TDD when required: vertical TDD; public-interface behavior test, red -> green -> refactor.

Reviewer: handoff, diff, evidence, Crew context, baseline/packet. Check handoff compliance, scope drift, evidence verdict, quality, reconciliation. Return `APPROVE`, `BLOCK`, or `COMMENT`; blockers separate from observations. Approval does not close gate.

On the engine: the reviewer runs a `survey` checklist — visit every check, `append` more from the handed-down context, record pass/fail without stopping, then `consolidate` to a verdict (the engine refuses `APPROVE` over an open `fail`). The implementer may drive its own `gated` plan to stay organized; that plan is self-authored, full of primitives, and never handed further down.

Use `DEFAULT_CHECKLIST.md` only for multi-step Crew recovery; one-shot work uses handoff + result.

Templates: `templates/IMPLEMENTER_PLAN.template.json` (gated, implementer's own plan), `templates/REVIEW_SURVEY.template.json` (survey, reviewer's checks), `templates/IMPLEMENTER_RESULT.template.md`, `templates/REVIEW_RESULT.template.md`. References: `references/role-scope.md`, workbench `references/checklist-engine.md`.
