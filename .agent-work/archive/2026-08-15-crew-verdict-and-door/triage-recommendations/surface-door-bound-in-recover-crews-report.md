# Triage Recommendation: `surface door_bound in recover_crews.py's human-facing report`

## Classification
`feature` (small, follow-on to this run's own hardening)

## Source checklist/artifact
- g2 REVIEW_RESULT (`.agent-work/crew-verdict-and-door/crew-handoffs/g2-reviewer-result.md`), non-blocking triage flag.

## Structural anchor
`scripts/recover_crews.py`

## Cartographer mismatch class
None.

## Desired behavior
- **Desired:** `recover_crews.py`'s human-facing summary line for each registry entry names whether that crew's door was bound (reusing this run's new `entry["door_bound"]` field), so a resumed/relaunched Commander or a human debugging a stalled crew sees the hazard without having to separately consult `crew-runs.json`.
- **Today instead:** `recover_crews.py` reports state (`active`/`resumable`/`needs-abandon`/`conflict`) without mentioning door-binding at all; a reader must cross-reference `crew-runs.json`'s new `door_bound` field by hand.
- **Type:** `measured` — read `scripts/recover_crews.py`'s current summary-line construction; confirmed no reference to `door_bound` or any door-binding concept.
- **Rev:** `35f6c663` (this run's HEAD; `door_bound` did not exist before this run's g2).

## Possible fix
Append `, door unbound` (or similar) to a summary line when `entry.get("door_bound") is False`, mirroring how `_crew_status_line` in `run_crew.py` already appends a `(blocked at ...)` suffix for blocked crews.

## Recommended priority
`low`

**Reason:** Cosmetic/visibility improvement on top of an already-shipped hardening (g2); the underlying hazard is already recorded in the registry, this only makes it easier to see without a second file read.

## Related artifacts
- `.agent-work/crew-verdict-and-door/crew-handoffs/g2-reviewer-result.md`
- `.agent-work/crew-verdict-and-door/REPLAN_INPUT.json` (`wave_forecast`)

## Disposition
`recommend-and-defer`

**Detail:** `recommend-and-defer: this run's launch order grants no tracker-filing authority, and scripts/recover_crews.py is outside the file-ownership fence (scripts/run_crew.py + tests only).`

## Issue creation authority
`issue-ready only`
