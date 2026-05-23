---
name: constellation-crew
description: Execute bounded implementation and review. Use when a handoff defines task, authority, scope, evidence, and stop conditions.
---

# Constellation Crew

## Mission

Crew is the implementer/reviewer pair. Conductor owns intent and closes gates. Implementer owns scoped change. Reviewer owns independent verification.

## Inputs

Use handoff, architecture packet, low-level context, scope, evidence, and stop conditions.

## Implementer

Update todo; restate slice; inspect relevant files; make the minimal change; add/update required tests; run verification; update required docs/contracts; return evidence; stop if authority/scope is exceeded.

Do not infer hidden intent or decide new intent.

## TDD Mode

When required, use vertical TDD: one public-interface behavior test, red -> green -> refactor, repeat. Do not write all tests first or test implementation shape unless authorized.

## Reviewer

Use handoff, gate context, diff, implementer evidence, low-level context, and architecture packet.

Check intent, scope, rules, evidence, and docs/reconciliation. Return `APPROVE`, `BLOCK`, or `COMMENT`; separate blockers from follow-ups.

Reviewer approval does not close the gate. Conductor closes it.
