# Triage Recommendation: `test_post_door_never_raises_on_junk lacked a len(rows) >= N assertion`

## Classification
`missing test`

## Source checklist/artifact
- Review finding, `g1-review` (`.agent-work/stop-hook-door-binding/crew-handoffs/g1-review-reviewer-result.md`, "Out-of-scope observations").

## Structural anchor
`tests/test_spine_rail.py::test_post_door_never_raises_on_junk`

## Cartographer mismatch class
None.

## Desired behavior
- **Desired:** the fuzz test asserts a minimum row count, matching its sibling
  `test_post_tool_use_never_raises_on_junk` (`assert len(rows) >= 12`) — so a future edit that
  accidentally empties or filters `rows` down to nothing still fails loudly instead of vacuously passing.
- **Today instead:** the new door-path fuzz test had no such assertion; `rows` was a 7-item literal, so the
  risk was low, but the convention its sibling established was not carried over.
- **Type:** `measured` — read the two test bodies side by side.
- **Rev:** as of this run's `g1-implement`/`g1-review`, before this fix.

## Recommended priority
`low`

**Reason:** low risk (a literal list, not a derived/filtered one), but it is the exact "a check that cannot
fail" shape this repo's own doctrine names, and the fix is one line.

## Related artifacts
- `.agent-work/stop-hook-door-binding/crew-handoffs/g1-review-reviewer-result.md`

## Disposition
`fixed-now`

**Detail:** `fixed-now: added "assert len(rows) >= 7" to test_post_door_never_raises_on_junk; committed
in this run's archive commit (scripts/hooks/spine_rail.py's own gate). Re-ran python -m pytest -q
tests/test_spine_rail.py after: 139 passed, 1 skipped -- unchanged count, confirms the addition is inert
except as a regression guard.`

## Issue creation authority
`issue-ready only`
