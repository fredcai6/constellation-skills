# Launch Order 4: `cleanup-f-derive-worktree — #609` (leg 4, the closeout leg)

Your predecessor parked this lane correctly. Read its return first — it is the
best-measured handoff any lane has produced today, and everything below assumes
you have read it.

## Read these, in this order

1. **`STATE_NOTE.md`** — leg 3's handoff. It is current and it is accurate; I
   checked its two factual corrections myself and both hold. Work from it.
2. **`ADMIRAL_RULING-3.md`** (this order's companion, below) — my answer to the
   one question leg 3 left me, plus what changed outside the lane.
3. `ADMIRAL_RULING-2.md`, `ADMIRAL_RULING-1.md` — still governing.
4. `LAUNCH_ORDER.md`, `PROBLEM_STATEMENT.md`, `MISSION_FRAME.md` — the frame.

## Leg 3 did not fail

`run_crew.py` recorded `attempt-3 -> failed` because the result artifact was not
written. It was not written because the engine's context governor told the
commander to close its gate carrying a digest and stop, and it did exactly that.
**g2 is closed with an APPROVE.** The lease is deliberately still held, at
`commander-cleanup-f-derive-worktree`.

Re-claim under that same id. **Never `--force`** — `--force` is a takeover of
someone else's lease, and this one is yours to resume.

Two consequences of resuming rather than starting:

- The lease's `last_heartbeat` will read badly stale (hours). **You are not
  blocked by it.** `require_session` returns early when the caller is the lease's
  own owner. The staleness is my finding, not yours, and its cause is named in
  the ruling below. Do not "fix" it, do not `--force` around it.
- #601 re-stamps `claimed_at` on a re-claim, so you inherit a fresh context
  reading rather than leg 3's 24%.

## What you owe, in order

Leg 3 sequenced this and I am not re-sequencing it. Its list is the order:

1. **`g3-implement`** — the half of #609 that matters. Its handoff is written and
   current at `crew-handoffs/g3-implementer-handoff.md`. **Re-measure the
   baseline into it before you dispatch.**
2. **`g3-review`**, then integrate.
3. **`skip` g4** with R2 as the recorded reason, **`skip` g5** with R3.
4. **reconcile** — three prose repairs, all this lane's own debt. See the ruling
   on the third.
5. **triage** — `tc1`–`tc12` are recorded in `execute.json`.
6. **review, feedback, archive.** Park at `archive`. **Do not merge** —
   publication is mine, and nothing is queued behind you.

## Baselines

`main` is still at **`17c2cee5`** — nothing has landed since leg 3 measured it.
Leg 3 verified it independently in an isolated clone at **3171 passed / 7 skipped
/ 0 failed**; this branch measured **3170 / 5 / 0** with an empty failure-set
difference both ways. Re-measure at your gate rather than citing those.

## Handing off again is allowed

If your context is genuinely spent, close the gate you are in, write the digest,
and stop — exactly as leg 3 did. Four lanes finished that way today and this lane
has now done it twice without losing a measurement. Running long to avoid a
handoff is the failure mode, not the handoff.
