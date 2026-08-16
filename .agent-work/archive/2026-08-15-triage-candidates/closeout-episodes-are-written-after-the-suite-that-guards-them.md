# Triage Recommendation: `closeout episodes are written after the suite check that guards them`

## Classification

`process` / `unverifiable-by-construction` — a gate order that guarantees an artifact escapes its own check.

## Source checklist/artifact

Observed 2026-08-15 in three independent lanes of the post-epic-568 wave:
`tc1-windows-path-form`, `tc1-episode-rewording` (which existed *only* to clean up the first), and
`launcher-hygiene`.

## Structural anchor

`tests/test_episode_observations.py::RealStoreTests` (the guard) against the Commander spine's gate
order: the full-suite check is a postcondition of an **integrate** gate, while episode records are
authored at **closeout** — strictly later.

## Cartographer mismatch class

None. The guard is correct and the gate order is defensible. Their composition is the defect.

## Observations

### Observation 1 — the ordering makes self-verification impossible

A lane runs its cache-clean full suite to satisfy an integrate postcondition, reports green, and *then*
writes its closeout episode records. Those records are inside `episodes/active/`, which
`RealStoreTests` scans. **The green the lane reported can never have covered the episodes it had not yet
written.**

`launcher-hygiene` reported `3031 passed, 6 skipped, 0 failed`. An Admiral re-measurement of the same
tree minutes later returned `2 failed`:

```
OFFENDER launcher-hygiene-001 a5 (workaround)        imperative: 'read'
OFFENDER launcher-hygiene-002 a3 (observed-behavior) second-person: 'you'
OFFENDER launcher-hygiene-003 a5 (workaround)        imperative: 'Read'
```

Both reports were honest and both were accurate at the moment they were taken.

**Type:** `measured` — both suite runs are on disk.

### Observation 2 — warning the lane does not prevent it

`launcher-hygiene`'s launch order carried an explicit section stating that closeout episodes face this
guard, that `workaround` / `proposed-remedy` statements must not open a clause with a bare verb, and that
the exception list was not available to it. It tripped all three anyway.

This is the same pattern as the auto-backgrounding defect
([`auto-backgrounding-breaks-the-foreground-crew-dispatch-contract`](auto-backgrounding-breaks-the-foreground-crew-dispatch-contract.md)):
a warning cannot substitute for a check the agent is able to run. Here the agent **could not** run it —
at the moment it wrote the episodes, its verification step was already behind it.

**Type:** `measured` — the order and the offending records are both on disk.

### Observation 3 — it has already cost a dedicated lane

`tc1-episode-rewording` existed solely to reword two statements that `tc1-windows-path-form` had written
at closeout, which blocked PR #588. That is one full dispatch spent on an artifact the authoring lane had
no opportunity to check.

**Type:** `measured` — the lane, its launch order, and its commits exist.

**Field notes**

The failure surfaces at the **worst** moment: after the lane has archived, released its lease and pushed,
so the PR is already open and the only remaining actor is the merging Admiral. It reads as a late,
mysterious regression in a branch that was green minutes earlier — and an Admiral who trusts the lane's
own report merges a red branch.

Three lanes tripped it in one day; a fourth was spent cleaning up after one of them.

## Desired behavior

A lane should be able to verify every artifact it authors. Either the episode guard runs after episodes
are written, or episode authoring moves before the verifying check.

## Possible fix

Cheapest first:

1. **Give the guard a fast standalone form and make closeout run it.** Add
   `python -m pytest -q tests/test_episode_observations.py` (sub-second) as a postcondition of the gate
   that *writes* episodes, rather than relying on the full suite that ran earlier. Smallest change,
   closes the hole exactly where it opens.
2. **Have `apply_episode_delta.py` refuse an offending statement at write time.** The store already has
   one writer; validating there makes the bad record unwritable rather than merely detected later. This
   is the strongest version and matches the existing "one write path" design.
3. Reorder closeout so episode authoring precedes the final verifying check. Larger blast radius;
   mentioned for completeness, not recommended.

Rejected: telling every Admiral to re-run the suite after a lane reports green. That is the current
workaround, it caught all three instances, and it will be forgotten — it also only works because the
Admiral independently re-measures, which is a habit rather than a mechanism.

## Open questions

- Does any other closeout-authored artifact sit inside a suite-scanned surface? Episodes are the one
  found today, but the same shape would apply to anything written after the integrate check.
- Is `apply_episode_delta.py` actually the sole write path in practice, or do lanes hand-edit the
  markdown? Option 2 depends on the answer.

## Recommended priority

**Medium-high.** Not a correctness risk in shipped code, but it produces a **red branch from an honestly
green report**, at the point of merge, and has already consumed a full dispatch. Its cost is entirely in
Admiral time and dispatch cycles, and it recurs with every lane that closes out.

## Related artifacts

- `.agent-work/triage-candidates/auto-backgrounding-breaks-the-foreground-crew-dispatch-contract.md` —
  same "warning is not a check" shape.
- `episodes/active/launcher-hygiene-00{1,2,3}.md` — the current offenders.

## Disposition

**recommend-and-defer**

**Detail:** `recommend-and-defer: surfaced 2026-08-15 during the post-epic-568 wave; no tracker-filing
authority exercised.`

## Issue creation authority

Not exercised.
