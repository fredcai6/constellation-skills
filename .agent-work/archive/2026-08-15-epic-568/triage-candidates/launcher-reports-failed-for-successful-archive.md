# Triage Recommendation: `the crew launcher reports failed for a successful archive`

## Classification

`infrastructure` / `false-signal`

## Source checklist/artifact

Observed 2026-08-15 during `epic-568-wave-2-repair`, crew
`constellation/epic-568-530/archive/commander/attempt-1`. Recorded in
`.agent-work/epic-568/ADMIRAL_LOG.md`.

## Structural anchor

`scripts/run_crew.py` (completion is judged by the existence of the `--result` artifact) against the
`archive` gate in `scripts/checklist_engine.py`, which relocates the work area.

## Cartographer mismatch class

None. Two components each behave as documented; the contract between them is what is wrong.

## Observations

### Observation 1

`run_crew.py` was dispatched with
`--result .worktrees/epic-568-530/.agent-work/epic-568-530/ARCHIVE_RESULT.md` and exited reporting
`crew constellation/epic-568-530/archive/commander/attempt-1 -> failed`.

### Observation 2

The archived spine at
`.worktrees/epic-568-530/.agent-work/archive/2026-08-14-epic-568-530/spine.json` shows
`archive: complete`, `blockers: 0`, and the lease `released` at `2026-08-15T01:10:00Z` with takeover
provenance intact. The result artifact exists — at
`.agent-work/archive/2026-08-14-epic-568-530/ARCHIVE_RESULT.md`, because the `archive` gate moves the
whole work area, the result document included.

**Field notes**

The launcher checks a path that the gate it dispatched has just emptied. This is not an edge case:
**every** successful archive reports failure, because relocating the work area is what archiving *is*.
Only a failed archive can leave the result where the launcher expects to find it, so the signal is
not merely noisy — it is inverted.

The expensive direction is clear. An Admiral trusting the exit status relaunches a Commander onto an
already-archived lane, and the duplicate-guard does not object because the first attempt is recorded
as failed. The second Commander then finds no work area at the expected path, and what happens next
depends on how carefully it was written. Nothing in the registry says the lane is done.

This was caught only because the Admiral verifies spine state rather than launcher verdicts. That
habit should not be what stands between the run and a duplicate dispatch.

It is the fourth false signal of this run, after the stale bytecode cache
([`pycache-root-mismatch-guard`](pycache-root-mismatch-guard.md)), the foreign spine door
([`crew-dispatch-must-bind-the-spine-door`](crew-dispatch-must-bind-the-spine-door.md)), and an
Admiral measurement taken while a Commander was still live. All four manufactured a confident,
wrong answer rather than an obvious error.

## Desired behavior

A dispatch whose gate is terminal should be judged on the spine reaching a terminal state, not on an
artifact path that the gate itself relocates. The launcher already supports exactly this: its
`--spine` help text says a spine-only dispatch "is judged on its bound spine reaching a terminal state
(`spine_terminal`) instead of a result artifact."

## Possible fix

Prefer `spine_terminal` judging whenever `--spine` is given and the dispatched gate is terminal, even
if `--result` is also supplied; or resolve the result path through the archive relocation before
declaring failure. The smallest honest version: if the result artifact is missing but the bound spine
is terminal, report success and say which check decided it.

Rejected alternative: telling every Admiral to pass `--result` paths that survive archival. That
pushes a harness bug into every launch order and will be forgotten.

## Open questions

- Do other gates relocate artifacts the launcher watches, or is `archive` the only one?
- Should a `failed` verdict ever be recorded when the bound spine is terminal? That combination looks
  contradictory on its face and might warrant a refusal to record rather than a quiet mismatch.

## Recommended priority

**High.**

**Reason:** it inverts the completion signal for the one gate that ends a lane, and it invites
duplicate dispatch onto archived work with the duplicate-guard disarmed. The failure is silent and
confident.

## Related artifacts

- `.agent-work/epic-568/ADMIRAL_LOG.md` — the incident.
- `.worktrees/epic-568-530/.agent-work/archive/2026-08-14-epic-568-530/` — the archived work area,
  including the result document at its relocated path.

## Disposition

**recommend-and-defer**

**Detail:** `recommend-and-defer: no tracker-filing authority was exercised this run, and the current
contract authorizes no work beyond the wave-2 items.`

## Issue creation authority

Not exercised. The Admiral's delegated classes cover merge-to-main and repo hygiene, not tracker
creation.
