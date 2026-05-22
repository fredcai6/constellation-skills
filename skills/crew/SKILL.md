---
name: constellation-crew
description: Execute bounded implementation and independent review from conductor handoffs.
---

# Constellation Crew

## Mission

Crew is the implementer/reviewer pair.

```text
Conductor owns intent and boundaries.
Implementer owns scoped change.
Reviewer owns independent verification.
Conductor closes the gate.
```

## Implementer

Receives the subagent handoff, relevant architecture packet, `docs/agents/IMPLEMENTER_REVIEWER_CONTEXT.md`, allowed scope, required evidence, and stop conditions.

Responsibilities:

1. Create/update local todo.
2. Restate task slice.
3. Inspect only relevant code/tests/docs.
4. Implement minimal change.
5. Add/update required tests.
6. Run required verification.
7. Return evidence.
8. Stop if authority/scope is exceeded.

The implementer does not decide new intent.

## Reviewer

Receives the original handoff, relevant framing excerpt, gated plan gate, diff/changed files, implementer evidence, low-level context, and relevant architecture packet.

Responsibilities:

1. Create/update local todo.
2. Check task intent match.
3. Check scope discipline.
4. Check rule compliance.
5. Check evidence sufficiency.
6. Check docs/reconciliation need.
7. Return `APPROVE`, `BLOCK`, or `COMMENT`.

Reviewer approval does not automatically close the gate. Conductor performs a light gate-closure check.
