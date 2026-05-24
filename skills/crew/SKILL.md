---
name: constellation-crew
description: Execute bounded implementation and review. Use when a handoff defines task, authority, scope, evidence, and stop conditions.
---

# Constellation Crew

Implementer owns scoped change. Reviewer owns independent verification.

Use handoff, Crew context, structural baseline / packet if provided.

Handoff completeness: verify task, intent, allowed scope, specific exclusions, required evidence, test mode, stop conditions, and return format. If missing, contradictory, impossible, or too broad: stop/report. Do not infer hidden intent.

Crew does not route, does not create issues, does not close gates, and does not expand scope. Return out-of-scope observations to Conductor.

Implementer: minimal change; required tests/docs/contracts; verification; evidence; stop if authority/scope exceeded.

TDD: when required, vertical TDD: public-interface behavior test, red -> green -> refactor.

Reviewer: use handoff, diff, evidence, Crew context, structural baseline / packet if provided. Check handoff compliance, scope drift, evidence verdict, code/doc quality, reconciliation concerns. Return `APPROVE`, `BLOCK`, or `COMMENT`; separate blockers from observations. Reviewer approval does not close gate.
