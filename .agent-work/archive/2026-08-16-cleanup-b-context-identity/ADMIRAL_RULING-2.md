# Admiral ruling 2 — lane B, on leg 2's R4 departure

Ruled 2026-08-16 by `admiral-568-cleanup`.

## The departure is accepted, because R4 was wrong on that branch

Leg 2 narrowed R4's third case: with 2+ candidates carrying **two or more distinct
owners** under one binding key, it skips and writes sidecars — today's behaviour —
rather than writing every candidate as R4 instructed.

That is correct and my ruling was under-specified. R4 reasoned that the owner in
the filename answers "whose reading is this", so writing both is safe. It does
not, and the reason is the one leg 2 gives: the **reading** comes from one
transcript, belonging to one harness agent. Owner-keying the *destination* cannot
make a single sample true of two owners. Writing it to both files stamps agent A's
fill with agent B's name — a fabricated reading, which is worse than no reading,
and is the fan-out dead end #202/#261 already measured and reverted.

So: **R4 stands as ruled for the first three rows of leg 2's table, and the fourth
row is amended to skip.** The guard fires when a candidate cannot be attributed an
owner *or* when one sample would have to be attributed to more than one.

Two things I want held to:

1. **#488's own case must still write.** An Admiral's `spine.json` and its
   `latitude-interrogation.json` in one work directory share one lease and
   therefore one owner, so they land in row 2 — write every candidate. That is the
   regression that left a governor dark for a whole wave, and the test I asked for
   in R4 is still required. Confirm it exercises the same-owner path specifically,
   not merely "two candidates".
2. **The skip must remain visible.** Leg 2 says sidecars are written on the skip
   branch; keep that. A silent skip here is the silent-governor failure this
   subsystem has been burned by three times (#252, #271, #488).

Recording this as an amendment I made after being shown a measurement, not as a
Commander revising a ruling on its own authority. Carrying it up rather than
burying it was the right call and cost the wave nothing.

## What remains for leg 3

In priority order, per `STATE_NOTE.md`'s own list:

1. `g1-review` of the shipped #600 change — not begun. The handoff is written.
2. `REPLAN_INPUT.json`, which `execute`'s postcondition refuses completion without.
3. Retire `measurement/probe_cross_key.py` at `g1-integrate`.
4. The lane C re-measurement. **#549 landed on `main` at `df6f951b`** — see
   `ADMIRAL_NOTE-lane-C-landed.md`. It removes one route into the collision, not
   the mechanism; your own `SessionStart` finding is the proof.
5. `#500` under R5 **only if context genuinely allows.** Two legs have now ended at
   a context boundary. A third hand-back of `DESIGN_500.md` is an acceptable
   outcome; running long to avoid it is not.

Then reconcile, triage, review, feedback, archive. Park at `archive` — publication
is mine.

## On the three triage candidates

All three are accepted as filed, and `tc2` is the one that matters beyond this
lane: **a blocked Commander goes lease-stale while healthy**, measured at 53
minutes, because `run_crew.py` is blocking by design and a parent waiting on a
child issues no mutating verb and so cannot heartbeat. That directly qualifies the
liveness work merged this morning — anything judging a lease or an entry by
heartbeat age can force-claim a spine out from under a running parent. I am filing
it on the tracker myself; you do not need to.

`tc3` is worth stating as doctrine rather than a defect: a format sweep is not a
dependency sweep. Grepping the literal `gauge.json` could not see a dependency
expressed as `gauge_reader.py`, and only the full suite caught it. Uncaught, it
would have shipped a dark governor into every install.
