# Triage candidate: an Admiral spine can lose its lease mid-run, and nothing surfaces it

**Status:** not filed. Held to closeout per the epic's standing ruling.

**Found by:** the Admiral of epic-567-door, 2026-08-17, **by accident** — during an unrelated
repo-hygiene survey, roughly four hours into a run in which the lease had been claimed at the
start and used continuously.

**Proposed pairing:** **#615** (*"a spine with no active lease has no ownership guard at all —
never-claimed or released"*) and **#552** (*"archiving a finished run never releases its lease"*,
whose fix makes archiving release one).

## Observed

`.agent-work/epic-567-door/spine.json` carried **no active lease**. The lease had been claimed
through the door at session start (`claimed lease constellation/epic-567-door -> active`) and
every subsequent mutating call had succeeded. Re-claiming returned:

```
resumed lease constellation/epic-567-door (heartbeat refreshed, claim re-stamped)
```

so the engine recognised the identity and restored it rather than treating it as a new claim.

Alongside it, two directories that should not exist, both timestamped `11:06` — the window in
which wave-2 lanes were running their `archive` gates:

- `.agent-work/archive/epic-567-door/cmdr-g/`
- `.agent-work/epic-567-door/epic-567-door/cmdr-g/`  ← **nested inside the live epic work area**

## Hypothesis, explicitly not a measurement

`durable_root()` (`scripts/agent_work_root.py`) returns a crew's **own worktree** root while an
Admiral epic lease is held, and the **main checkout** when it is not. Lane G's #552 change makes
an `archive` release a lease. So: if the epic lease lapsed, every live lane's durable root would
flip to the main checkout, and their archive-time writes would land in the Admiral's work area
under the epic's own id — which is exactly the shape of the two stray directories.

**This is a hypothesis.** It was not reproduced, and the causal direction (did the lapse cause
the stray writes, or did an archive cause the lapse?) is not established. It is written down
because the alternative — leaving an unexplained lease lapse unrecorded — is worse.

## Why it matters independently of the cause

**#615 is usually read as "an unclaimed spine is unguarded."** This is the other end of it: a
spine that *was* claimed can become unclaimed while its holder is still working, and **nothing
tells the holder.** Every mutating verb kept succeeding, because an unleased spine has no
ownership guard — which is precisely #615's complaint, now demonstrated against a live run rather
than a fresh one.

The Admiral only noticed because it happened to run `git status` for unrelated reasons. A run
that never looked would have finished its epic believing it held a lease it did not hold, and
`closeout`'s terminal provenance check — which requires the lease to cover every journaled
action — would have failed at the very end, with no way left to explain the gap.

## Recommended remedy shape

Either a mutating verb should refuse (or at minimum warn) when the caller's identity no longer
holds the lease it started under, or lease loss should be journaled as an event rather than
being a silent state change in a JSON field. The first is a guard; the second is provenance.
Both are cheaper than an unexplained gap at closeout.
