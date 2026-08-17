# Constellation Status Model

Retired as a taught procedure (issue #565) except for the two sections below, which stay
load-bearing: `Crew Return Status` is pinned verbatim by `tests/test_commander_evidence_convention.py`
and cited by `skills/commander/templates/IMPLEMENTER_HANDOFF.template.md`; `Review Verdict` is
the field `skills/reviewer/templates/REVIEW_RESULT.template.md` and
`skills/implementer/templates/IMPLEMENTER_RESULT.template.md` both point at by name. Gate status
is directly observable from the engine's own `current` output (`global-everyone.md`, "Engine
output is the state channel") and needs no separate table; Commander Gate Decision vocabulary
is uncited internal prose, not an engine-enforced convention.

## Crew Return Status

Use for implementer/reviewer result status:

```text
complete | partial | blocked | out-of-scope | failed
```

Rules:

- `partial` requires completed portion, missing portion, and next action.
- `blocked` requires blocker and needed authority/evidence.
- `out-of-scope` requires scope concern and return-to-Commander note.
- `failed` requires failure evidence and recommended recovery.

## Review Verdict

Use for reviewer judgment:

```text
APPROVE | BLOCK | COMMENT
```

Rules:

- `APPROVE` means no blockers found against handoff, evidence, scope, and project rules.
- `BLOCK` requires blockers.
- `COMMENT` means observations only; gate may still need Commander decision.
