# Triage Recommendation: whether to tighten `tests/test_validate_spine.py`'s `falsifiable-all-null` floor to zero-tolerance blocking

## Classification
`unresolved decision`

## Source checklist/artifact
- epic-569/w3-promote g8-validate-spine-wiring-and-docs

## Structural anchor
`path: tests/test_validate_spine.py`

## Cartographer mismatch class
`none`

## Desired behavior
- **Desired:** a possible future state where `tests/test_validate_spine.py` blocks (zero-tolerance,
  mirroring `TestShapeAcceptsEveryShippedTemplate`'s already-blocking pattern) on any
  `falsifiable-all-null` fault across the 8 templates `epic-569/w3-promote` owns, rather than the
  current floor-style `>= N` assertion that only regresses on a fault *count increase*.
- **Today instead:** the floor is a regression guard (`>= 13`, updated gate-by-gate this wave as
  real promotions cleared gates), not a zero-tolerance gate. Several remaining all-null gates are
  honestly-declined by design (`IMPLEMENTER_PLAN.template.json`'s `m1.c1` most of all — a
  *self-declared* unpromotable TDD-red condition, not a defect), and 2 separate
  `falsifiable-unresolved-placeholder` faults (see the companion triage recommendation) sit outside
  this lane's promotion scope entirely — a zero-tolerance tighten would need those resolved first
  or would need to special-case them, and this wave declined to do either.
- **Type:** `measured` — `python3 -m pytest tests/test_validate_spine.py -q` → `103 passed`;
  `discover_checklist_templates` + `validate_file` sweep → `{'falsifiable-all-null': 13,
  'falsifiable-unresolved-placeholder': 2}`, matching the floor exactly (no drift).
- **Rev:** `epic-569/w3-promote` branch, commit `4d92dc45`.

## Open questions
- Should the zero-tolerance tighten special-case `IMPLEMENTER_PLAN.template.json`'s `m1.c1`
  permanently (since it is structurally, not just currently, unpromotable), or should
  `validate_spine.py`'s own `falsifiable-all-null` rule gain a documented escape for a
  self-declared-unpromotable condition so future templates with the same TDD-red shape don't hit
  the same wall?
- Does resolving the 2 `falsifiable-unresolved-placeholder` faults (companion recommendation) come
  first, or can the zero-tolerance tighten scope itself to `falsifiable-all-null` only and ignore
  the placeholder code entirely?

## Recommended priority
`low`

**Reason:** the floor already does its regression-guard job correctly (kept current gate-by-gate
this whole wave); tightening it further is a design decision with real edge cases, not a defect.

## Related artifacts
- `.agent-work/w3-promote/notes-1.md` g8 section
- `.agent-work/w3-promote/RESULT.md` §5
- `.agent-work/w3-promote/crew-handoffs/TRIAGE-unresolved-placeholder-faults.md` (companion)

## Disposition
`recommend-and-defer`

**Detail:** `decision:validate-spine-wiring-is-in-scope`'s own settle clause named this exact
decision as "decide with the Admiral" — no reachable human/Admiral this gate (delegated mode);
recorded as a user-decision evidence item at g8 citing that section, disposition confirmed here
rather than re-litigated.

## Issue creation authority
`issue-ready only`
