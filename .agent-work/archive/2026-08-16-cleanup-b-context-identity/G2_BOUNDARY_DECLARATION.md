# `g2-implement-500` boundary declaration — HAND BACK

Declared at the boundary, before any work started, per the gate's own c1 and
`ADMIRAL_RULING-1.md`'s Scope section ("say so at the boundary rather than
running long").

## The decision

**HAND-BACK branch.** No code ships for #500 this wave. `DESIGN_500.md` is
returned as the deliverable for the third time, and it remains accepted and
unchanged.

## The context reading it rests on

Not an estimate. The engine refused the gate, in these words:

```
REFUSED: g2-implement-500: context at 17% is at/over the hard limit, so this is
not the moment to BEGIN work here — finish and close the gate you are already
in, then request a refresh so a fresh agent starts this one.
```

The reading behind it, from this leg's own owner-keyed gauge file
`gauge-commander-cleanup-b-context-iden-88c76234484d.json`:

```json
{"schema_version": 1, "fill_fraction": 0.166613, "model": "claude-opus-5",
 "observed_at": "2026-08-16T14:47:36.035Z",
 "owner": "commander-cleanup-b-context-iden-88c76234484d"}
```

Two things are worth stating plainly about that reading.

First, **it is provably this leg's own.** It carries an `owner` field naming this
Commander, and it sits in a file keyed to that owner. Before this wave the same
trip would have been unattributable — the reading could have been any of the
three harness keys bound to this spine. The change #600 shipped is what makes
this declaration evidence rather than assertion. The lane's own governor is
governing the lane.

Second, **it is the same guard, at the same reading, that ended leg 2** — leg 2
was refused entry to `g1-review` at 17%. This leg spent its budget on
`g1-review`, `g1-integrate`, and the probe/lane-C measurement work, and arrives
at #500's door with the same answer leg 2 got at its own door.

## Why hand back rather than push

The gate's imperative forbids the failure mode directly: "Do not start the code
branch and abandon it mid-way." #500 is not a small change. It is a
**refuse-where-we-currently-permit** change — normally outside inherited latitude
and authorized only by R5 — that touches `checklist_engine.py`'s **claim path**,
which the frozen order fenced. It needs an implementer crew, an independent
review, and red-before/green-after evidence against the real engine. Beginning
that at 17%, with five spine steps (`reconcile`, `triage`, `review`, `feedback`,
`archive`) still owed and the Admiral's instruction to **park at `archive`**,
would mean abandoning it mid-way with near-certainty.

`LAUNCH_ORDER-3.md` settles the trade explicitly: "An accepted limit reported
plainly is worth more to me than a rushed implementation of a design that is
already settled." `ADMIRAL_RULING-2.md` agrees: "A third hand-back of
`DESIGN_500.md` is an acceptable outcome; running long to avoid it is not."

## What is being handed back, and what it already settles

`DESIGN_500.md` is **accepted and complete as a design**. It is not a sketch and
it does not need re-deriving. It answers `decision:consume-on-lease-change`'s
settle condition with an explicit verdict rather than a restatement (the gate's
c2 checks this mechanically and it passes), and it records that the settle
experiment was **run**: `@grade: settled/measured`.

R5 already decided the shape — **option (a)**: a re-claim retires the claiming
agent's own pending refresh-request, so its next `start` is refused where today
it is released. Option (b), exempting a same-`session_id` re-claim, is
**declined** by the ruling, because it preserves today's behaviour by refusing to
serve the one case #500 exists for.

So the next leg does not inherit an open question. It inherits a settled design,
a settled decision, and a named authority.

## What the next leg picks up

1. **`g2-implement-500`, ship branch.** Implement `DESIGN_500.md` as written; do
   not re-derive it. The report must say two things explicitly: that **R5 is the
   sole authority** for a refuse-where-we-permit change, and that R5 plus the
   ruling's "refresh regions" scope is the sole authority for touching the fenced
   claim path.
2. **Its evidence standard is unchanged**: red-before / green-after over
   behaviour, against the real engine, with no patched internals. The settle
   assertion named in `DESIGN_500.md` is that a relaunched agent's first
   `current` shows no `REFRESH REQUESTED:` line while an un-reclaimed spine still
   shows one.
3. **What #500 inherits from #600**, now that it is integrated: one owner-key
   definition in `gauge_reader.py`, and an engine that resolves the gauge owner
   from its own active lease `session_id`.

## What this leg is NOT handing back

Everything else in the lane is finished. #600 is shipped, independently
reviewed (`APPROVE`), and integrated with a **zero** failure-set difference
against a `main` baseline re-measured at gate time. Both of `g1-integrate`'s
gate-owned jobs are done and measured rather than assumed — the probe now
asserts the post-fix world, and the lane C re-measurement confirms #549 removed
a route and not the mechanism. The remaining spine tail is this leg's to drive.

_Declared by `commander-cleanup-b-context-identity`, leg 3, 2026-08-16._
