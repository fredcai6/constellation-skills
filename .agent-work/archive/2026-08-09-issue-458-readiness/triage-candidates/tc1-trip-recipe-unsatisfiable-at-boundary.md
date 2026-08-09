# Triage Recommendation: HARD-trip refresh recipe is unsatisfiable at a gate boundary

## Classification
bug

## Source checklist/artifact
- spine.json triage_candidates[tc1], raised at the `context` step by this work's predecessor session

## Structural anchor
scripts/checklist_engine.py (`_trip_advisory`, `_trip_hard_gate`) | none more specific — no map exists in this repo

## Cartographer mismatch class
none

## Problem
The HARD-band advisory tells an agent to close the gate it is "already inside," but the trip can
fire at a step **boundary** — the prior gate (`init`) already complete, the next gate (`context`)
still `pending`, never started. In that state the documented recipe is unsatisfiable: `advance`
refuses a pending gate ("must be in-progress to advance", recovery: `start`), and `start` is
exactly the verb HARD refuses ("not the moment to BEGIN work here"). The predecessor session hit
this directly, filed the refresh-request at `context` (`e-context-1`, `why_ref w-1`), and stopped
— there was nothing open to close.

## Current truth
The advisory text (`_trip_advisory` in `scripts/checklist_engine.py`) assumes the tripped agent is
mid-gate ("close THIS gate... A fresh agent picks up from your DIGEST"). `_trip_hard_gate` only
guards `start`/`reopen` (verbs that BEGIN work), and releases a begin when a matching
refresh-request is already pending. Filing the refresh-request against the not-yet-started gate
and then having a **fresh** agent `start` it (now released, since the request is pending) is what
actually resolved this in practice, once a fresh session picked it up — but nothing in the
advisory text says to do that; the fresh agent has to work it out from the mechanism itself.

## Desired/future concern
Either the advisory text should distinguish "mid-gate, close it" from "at a boundary, nothing is
open — file the request and stop, a fresh agent will `start` (released) the next gate," or the
doctrine reference (`references/global-everyone.md` §reach-up) should say explicitly that a
released `start` is the expected resolution at a boundary trip, not just an emergent property a
reader has to derive from source.

## Evidence
- This run's own `current` output at the `context` step showed exactly this: gate `pending`,
  `REFRESH REQUESTED: context`, advisory text worded for a mid-gate close.
- `TRIP LEDGER`/`TRIP HISTORY` in this run's spine record `start context -> begin-refused`
  followed later by `start context -> begin-released` once the refresh-request was on file.

## Impact
Every Commander relaunch that trips HARD exactly at a step boundary (not mid-gate) hits this same
unsatisfiable-recipe moment and has to reason it out from source rather than following the
advisory. Noted by the predecessor as "worth a look alongside #431/#467's other residuals" — the
governor/trip mechanism has had several rounds of fixes this epic (#419, #440, #488, #467); this
may already be a known residual there rather than a new gap.

## Suggested scope
Small: either reword `_trip_advisory`'s boundary-case text, or add one clarifying sentence to
`references/global-everyone.md` §reach-up about the released-start resolution at a boundary.

## Non-goals
Does not change `_trip_hard_gate`'s actual refusal/release logic — that behaved correctly once the
refresh-request was on file. This is a documentation/advisory-wording gap, not a mechanism bug.

## Acceptance criteria
- [ ] The HARD-band advisory (or its referenced doctrine) states the boundary case explicitly:
      what to do when the trip fires against a gate that was never started.
- [ ] A fresh agent hitting this can follow the advisory text directly without deriving the
      released-start behavior from `checklist_engine.py` source.

## Recommended priority
low

**Reason:** Workable today (this run and its predecessor both resolved it correctly by deriving
the mechanism from source), but costs every agent that hits it the same derivation.

## Related artifacts
- This run's spine.json `why_trail`/`trip_ledger` entries around the `context` gate
- `scripts/checklist_engine.py` `_trip_advisory`, `_trip_hard_gate`
- Possibly related: #431, #467 (cited by the predecessor as related governor work this epic)

## Disposition
recommend-and-defer

**Detail:** This run's launch order (`LO-w5-c2-readiness.md`) grants latitude to choose
script-vs-mode, define the readiness list, add tests, and open/push a PR/comment on #458 — it does
not grant issue-filing authority, and `scripts/checklist_engine.py` is explicitly crew 4's file
this wave, not this run's. Whether this duplicates #431/#467 residuals is also unclear without
reading those issues' current bodies, which is outside this run's scope. Deferred to the Admiral.

## Issue creation authority
ask user
