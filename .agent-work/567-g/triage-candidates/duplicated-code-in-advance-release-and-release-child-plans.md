# Triage Recommendation: minor duplication in two closeout primitives (Fowler, non-blocking)

## Classification
`cleanup`

## Source checklist/artifact
- g1-review (`.agent-work/epic-567-door/cmdr-g/crew-handoffs/g1-reviewer-result.md`), Fowler pass, flagged (non-blocking)
- g2-review (`.agent-work/epic-567-door/cmdr-g/crew-handoffs/g2-reviewer-result.md`), Fowler pass, flagged (non-blocking)

## Structural anchor
`scripts/spine_lifecycle.py` — `_advance_and_release`, `_release_child_plans`

## Cartographer mismatch class
none

## Observations

### Observation 1
- **What's wrong:** `_advance_and_release`'s three stages (start/advance/release) repeat the same call/check-code/return-refusal shape three times in a row.
- **Expected:** A small `_call_stage(argv, stage)` helper would give the shape one implementation.
- **Conditions:** Any read of `_advance_and_release`'s body.
- **Type:** `measured` — read directly by the g1 reviewer, confirmed by the Commander re-reading the same source.
- **Rev:** this worktree, uncommitted, base `600de020`, after g1/g2/g3 all landed.

### Observation 2
- **What's wrong:** `_release_child_plans`'s realpath-resolve-then-containment-check block (property 3, escape refusal) is repeated verbatim in its declaration loop and its scan loop.
- **Expected:** A small `_resolve_within(path, boundary)` helper would give property 3 one implementation instead of two.
- **Conditions:** Any read of `_release_child_plans`'s body.
- **Type:** `measured` — read directly by the g2 reviewer, confirmed by the Commander re-reading the same source.
- **Rev:** same as Observation 1.

## Possible fix
Two small private helpers (`_call_stage`, `_resolve_within`) inside `scripts/spine_lifecycle.py`, each replacing 2-3 repeated inline blocks. Both are pure refactors — no behavior change, and the existing test suite (119 tests, all currently green) should catch any regression if it's wrong.

## Open questions
None.

## Recommended priority
`low`

**Reason:** Both were explicitly Fowler-flagged as non-blocking by two independent reviewers, and neither affects correctness — the underlying safety properties (verbatim refusal passthrough, realpath containment) are independently tested and green. Deferred rather than fixed in this lane to avoid touching already-reviewed, integrated code without a fresh review pass.

## Related artifacts
- `.agent-work/epic-567-door/cmdr-g/g1-review/FOWLER_PASS.json`
- `.agent-work/epic-567-door/cmdr-g/g2-review/FOWLER_PASS.json`

## Disposition
`recommend-and-defer`

**Detail:** filing authority per `decision:no-issue-filing` — this lane files no issues; recorded here for the Admiral's disposal.

## Issue creation authority
`ask user`
