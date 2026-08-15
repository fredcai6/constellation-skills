# Triage Recommendation: `Reviewer's Fowler-pass record path collides across gates in one work area`

## Classification
`bug` / `missing test`

## Source checklist/artifact
- g2 reviewer's Workflow Feedback (`.agent-work/crew-verdict-and-door/crew-handoffs/g2-reviewer-result.md`).

## Structural anchor
`skills/reviewer/templates/` (the `r6-fowler` survey-item template, installed as `constellation-reviewer`)

## Cartographer mismatch class
None.

## Observations
### Observation 1
- **What's wrong:** The reviewer skill's `r6-fowler` survey item writes its Fowler code-smell record to `.agent-work/<work-id>/FOWLER_PASS.json` — scoped to the WORK-ID, not the GATE. In a multi-gate Commander run (this one: g1 then g2), the g2 reviewer's Fowler record silently overwrote g1's on-disk file at the identical path.
- **Expected:** Each gate's review should get its own Fowler-pass record (e.g. `.agent-work/<work-id>/<gate>-review/FOWLER_PASS.json`, alongside that gate's own `review.json`), so a later gate's review never clobbers an earlier gate's evidence file.
- **Conditions:** Any Commander run with 2+ crew gates in one work area, each independently reviewed.
- **Type:** `measured` — the g2 reviewer subagent reported this directly after observing its own Fowler record land at the same path g1's reviewer had already written to.
- **Rev:** `35f6c663` (this run; both g1 and g2 reviews ran in the same work area `.agent-work/crew-verdict-and-door/`).

## Desired behavior
See Observations — this is reported as a defect (data loss risk: g1's Fowler evidence is unrecoverable from disk after g2's review ran), not a pure enhancement.

## Possible fix
Gate-scope the Fowler-pass output path in the `r6-fowler` template, matching the existing gate-scoped `review.json` path (`.agent-work/<work-id>/<gate>-review/review.json`) the same template already uses.

## Recommended priority
`medium`

**Reason:** No functional harm THIS run (each `review.json` already embeds the Fowler command's output verbatim, so the consolidated verdict didn't depend on the now-overwritten file), but it is a silent data-loss pattern that will bite a future run needing to re-inspect an earlier gate's Fowler evidence after a later gate's review has run.

## Related artifacts
- `.agent-work/crew-verdict-and-door/crew-handoffs/g2-reviewer-result.md`
- `.agent-work/crew-verdict-and-door/FOWLER_PASS.json` (currently holds only g2's record; g1's was overwritten)

## Disposition
`recommend-and-defer`

**Detail:** `recommend-and-defer: this run's launch order grants no tracker-filing authority, and the constellation-reviewer skill's templates are outside the file-ownership fence (scripts/run_crew.py + tests only) -- this is a fix to the reviewer skill itself, not to run_crew.py.`

## Issue creation authority
`issue-ready only`
