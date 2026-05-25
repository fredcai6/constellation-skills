---
name: constellation-crew
description: Execute bounded implementation/review. Use when handoff defines task, authority, scope, evidence, stop conditions.
---

# Constellation Crew

Implementer owns scoped change. Reviewer owns independent verification. Use handoff, Crew context, structural baseline/packet if provided.

Handoff completeness: task, intent, allowed scope, specific exclusions, required evidence, test mode, stop conditions, and return format present/possible. Else stop/report. Do not infer hidden intent.

Crew does not route, does not create issues, does not close gates, does not expand scope. Return out-of-scope observations to Pilot.

Implementer: minimal change; tests/docs/contracts; verification; evidence; stop if authority/scope exceeded. TDD: when required, vertical TDD: public-interface behavior test, red -> green -> refactor.

Reviewer: handoff, diff, evidence, Crew context, structural baseline/packet if provided. Check handoff compliance, scope drift, evidence verdict, quality, reconciliation. Return `APPROVE`, `BLOCK`, or `COMMENT`; separate blockers from observations. Reviewer approval does not close gate.

Templates: `templates/IMPLEMENTER_RESULT.template.md`, `templates/REVIEW_RESULT.template.md`.
