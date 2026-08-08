## Wave 3 review

**Four issues, four merges, four closes -- and for the first time in this epic every PR carries an independently posted verdict on the forge.** Main is green at `1789 passed, 2 skipped, 683 subtests, exit 0` on the final merged tree.

| Issue | PR | Merge | What landed |
|---|---|---|---|
| #461 | #490 | `ad149283` | the episode-store control tests worktree-vs-index only |
| #488 | #491 | `8b9330ea` | the gauge writer dedups by distinct path |
| #489 | #491 | `8b9330ea` | the fixture resolver fails loudly on 2+ matches |
| #465 | #492 | `4da9bc9b` | the r6-fowler placeholder has an affordance; the engine writes bytes |

### The method, and what it found

Every launch order carried one instruction: **build the defective world and watch the current code get it wrong before fixing it**, because for all four issues green is what the broken version already does. The reviewers took it further than the orders asked.

- #491's reviewer noticed the negative-direction test **passes on both sides of the fix**, said so, and **disabled the skip branch** to prove the test had teeth.
- #492's reviewer mutated `save()` in **both** directions and found that **on Windows the CRLF fixture passes against the broken code** -- the obvious test for a CRLF bug is exactly the test that proves nothing here. The LF fixture is the discriminating one.
- #465's own cold critic caught that **its integrate gate could not fail**: the check was `pytest -q tests`, green on a suite that had never gained the new tests.

Six independent instances of one defect family in a single wave, two of them caught by crews inside their own process before shipping.

### The governor fixed itself in front of us

#488 was found on this Admiral, fixed by a crew it dispatched, and closed by watching the Admiral recover: `gauge-skip.json` vanished and a live reading appeared minutes after the merge, on the same two-binding configuration that had been silent for nine hours.

The reading is the finding. **33% fill** -- roughly double the 17-21% band at which every crew HARD-trips. The band is not mistuned; it is **role-blind**.

### Cost

Two governor trips, two clean recoveries, both costing bookkeeping only -- W3-C tripped at wrap-up with all work verified, W3-A with its PR already open. That is A2's round trip, run twice by hand, before A2 has an issue cut.

### Stopping here

The latitude contract expired at this boundary by its own terms. A2 is next and has no issue cut, which is a scope decision the human owns.
