# Triage candidate — the human-confirmation requirement sits in the mutable middle for two of three roles

**Not filed.** `decision:no-issue-filing-mid-run` — staged only. Raised by the independent
reviewer at gate g2 and confirmed by the Commander against the templates.

## Observation

`ADMIRAL_SPINE`'s `closeout` — now a frozen bookend — carries its own human-acceptance
postcondition: `c5, "epic summary accepted by the human", check: {kind: artifact, evidence_type:
user-decision}`. Freezing `closeout` therefore also freezes the requirement that a human accept.

`COMMANDER_SPINE`'s `archive` and `EXPLORER_SPINE`'s `route` are now frozen too, but neither
carries a human-decision postcondition. For a Commander the human-acceptance checkpoint lives at
`review`, which sits **inside the mutable middle** and is amendable away.

## Why it matters

The bookend freeze delivered by #634 guarantees a Commander run reaches `archive` — it cannot
terminate early. It does **not** guarantee a human ever accepted the result, because the gate that
asks for acceptance can still be dropped. The same probe that motivated #634 deleted `review`
alongside `archive` (`.agent-work/567-k/evidence/probe-closing-bookend.md`). `archive` is now
protected; `review` is not.

So the freeze is doing less than it may appear to: it protects the run's *completion*, not the
run's *acceptance*.

## Candidate remedy

Bake the human-decision postcondition onto the frozen closing bookend for Commander and Explorer,
the way Admiral's `closeout.c5` already does — rather than freezing more gates, which would eat
into the middle the human explicitly wanted squishy.

## Disposition

`recommend-and-defer`. Deliberately **not** taken this run: it changes what a Commander run must
prove before it can close, which is a doctrine-level change to the human-checkpoint rigor dial,
and that is the human's call, not a lane's. It is also strictly wider than #634's stated scope.

## Not claimed

I did not check whether any real run has closed without acceptance. This is a structural reading
of the three templates, not an incident.
