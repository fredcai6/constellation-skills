## Current planning truth — epic 569

**Intent.** Make a green qualitative gate mean something by telling the agent *what would count* at
plan time, rather than telling it at attest time that it got it wrong. The epic was filed as
enforcement — every work package ends in a refusal. A refusal adds work to the agent's plate at the
most expensive moment in the run. The same code buys the opposite when pointed at plan time: the
basis is declared while someone is thinking about what the gate means, and attest becomes *pointing*
rather than *composing*.

**The boundary that must not be crossed.** This epic must not add machinery that is itself unwired.

### Current wave (launching)

**Objective.** Guarantee that what this epic delivers is actually wired, and close the one gate in
the corpus that cannot pass.

- **`w1-wiring`** (#345 #444 #368) — census all 26 check-shaped scripts as live / unwired / dead with
  evidence per row, settle the `generate_spine.py` disposition, then lint **or** delete. A census
  showing mostly-dead code means deletions and no lint: that is an honest null and a complete
  deliverable, not a failed wave.
- **`w1-verdict`** (#371) — a `match` may name a set of acceptable values; a mistyped match shape is
  reported rather than becoming a silently unsatisfiable gate.

### Nonbinding forecast

1. Declared basis + evidence locators (#556 #557) — the epic's core value, entered once wave 1 has
   settled which spine-instantiation path is actually live.
2. Plan-freeze validation + journal fidelity (#518 #524 #381 #382 #459 #515 #390).
3. Reviewer machinery (#375 #358 #363 #259 #223 #388 #376 #221).

Forecast is provisional. The contract expires at the wave-2 checkpoint, where #558's review-level
doctrine is settled with the human before wave 3 dispatches.

### Live uncertainties

| Unknown | Settles by |
|---|---|
| Is the unwired-script population dead code or unwired capability? | wave 1 census — a mostly-dead answer refreshes the contract early |
| Does `generate_spine.py` have any live caller? | wave 1 path trace |
| Can a sonnet commander do this from a well-specified launch order? | wave 1 return quality and double-block count |

That third one is the epic's own thesis turned on itself: if a well-specified checklist cannot let a
smaller model do the work, the checklist is not taking enough off the agent's plate.
