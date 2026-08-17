# Triage Recommendation: reviewer's r6-fowler survey template breaks on nested work-ids

## Classification
`bug`

## Source checklist/artifact
- g1-review, g2-review, g3-review workflow feedback (all three, identically)

## Structural anchor
`skills/reviewer/templates/REVIEW_SURVEY.template.json` (installed copy; the reviewer's own bundled template), `r6-fowler`'s postcondition command

## Cartographer mismatch class
none

## Observations

### Observation 1
- **What's wrong:** The `r6-fowler` survey item's postcondition command assumes a flat `.agent-work/<work-id>/FOWLER_PASS.json` layout. A plain substitution of `<work-id>` with this project's actual nested work-id (`epic-567-door/cmdr-g/g1-review`, `.../g2-review`, `.../g3-review`) produces the wrong path — the reviewer's real review-state directory is `.agent-work/epic-567-door/cmdr-g/<gate>-review/`, not `.agent-work/<full-work-id>/`.
- **Expected:** The template's `c1` postcondition command resolves to the reviewer's own actual survey directory, wherever that is, without a manual repair step.
- **Conditions:** Any nested work-id (a Commander-dispatched reviewer whose work area sits under `.agent-work/<epic>/<commander>/`, not flat `.agent-work/<id>/`) — the live convention in this repo for every crew-dispatched review this run.
- **Type:** `measured` — hit and independently worked around, identically, by three separate reviewer crews (g1, g2, g3) in this same lane, each using the survey template's own documented REPAIR PATH (`amend --delta` with a `retext-check` op).
- **Rev:** this worktree, three separate crew dispatches, base `600de020`, 2026-08-17.

## Possible fix
Either parameterize the actual review-state directory into the template's instantiation step (so `c1`'s command is built from the reviewer's own resolved survey path, not a bare `<work-id>` token), or change the convention to a flat `.agent-work/<work-id>/` layout for Fowler-pass output specifically. Not evaluated which is better — a repo maintainer's call.

## Open questions
- Is the flat-layout assumption a template bug, or does the reviewer skill expect callers to always instantiate a flat work-id (making this project's nested convention the actual mismatch)? Worth settling before picking a fix.

## Recommended priority
`medium`

**Reason:** Non-blocking each time (the documented repair path works and was used successfully three times), but it is a real, repeatedly-measured defect that costs every reviewer crew in this kind of nested project the same detour. Three independent occurrences in one lane is a strong signal it will recur.

## Related artifacts
- `.agent-work/epic-567-door/cmdr-g/g1-review/`, `g2-review/`, `g3-review/` — each contains the `amend`-repaired survey and its `FOWLER_PASS.json`.
- `.agent-work/epic-567-door/cmdr-g/crew-handoffs/g1-reviewer-result.md`, `g2-reviewer-result.md`, `g3-reviewer-result.md` — each names the exact repair step taken.

## Disposition
`recommend-and-defer`

**Detail:** filing authority per `decision:no-issue-filing` — this lane files no issues; recorded here for the Admiral's disposal. Not this lane's file to fix (`skills/reviewer/` is outside this lane's ownership).

## Issue creation authority
`ask user`
