# Launch Order 2: `cleanup-b-context-identity — #600, #500` (relaunch, attempt 2)

> Write per `constellation-how-to-talk` — clear, concise, grounded.

You are the **second leg** of this lane, relaunched into the **same spine** by
`admiral-568-cleanup` after your predecessor blocked at `plan` and floated a
decision that has now been ruled.

## Read these three, in this order, before anything else

1. **`.agent-work/cleanup-b-context-identity/ADMIRAL_RULING-1.md`** — the answer to
   the float. R1 and R2 are the human's rulings; R3–R5 are the Admiral's. This
   supersedes the frozen order wherever they disagree, and it says exactly where.
2. **`.agent-work/cleanup-b-context-identity/LAUNCH_ORDER.md`** — the original
   frozen order. Everything in it still binds except as amended by the ruling:
   mission, file ownership, fences, merge gate, budget, return shape.
3. **`.agent-work/cleanup-b-context-identity/RESULT.md`** and `notes-b.md` — leg
   1's completed work. The measurement is **accepted and must not be redone**.

## What changed since the frozen order was written

- `decision:identity-not-time` is **amended** (ruling R1). Identity handles the
  concurrent case, time handles the sequential one. The frozen order's *"should end
  up unnecessary"* is withdrawn. Do not try to satisfy the original wording.
- `decision:consume-on-lease-change` is **settled** (ruling R5), no longer a guess.
- Two new rulings that were not in the frozen order at all: R3 (leaseless
  checklists keep today's behaviour) and R4 (the #488 ambiguity guard must not fire
  on differing owners, with a test in #488's own shape).

## The state you are inheriting

- `plan` is **blocked** in the spine, with the lease still active under
  `commander-cleanup-b-context-identity`. Your first spine action is to `resume`
  that gate — the block was a correct escalation, not a failure, and the thing it
  was waiting for has arrived.
- Re-claiming the lease under the same session name is now **safe and correct**:
  #601 makes a re-claim re-stamp `claimed_at`, so you will not inherit leg 1's
  context reading. Do **not** pass `--force`; that is a takeover of someone else's
  lease, and this one is yours.
- `plan`'s work is largely done: `MISSION_FRAME.md`, `execute.json`,
  `PLAN_ALTERNATIVES.md` and a cold critic pass all exist. Revise the plan to match
  the ruling rather than re-authoring it, and say in your report what you changed
  and why.

## Why you exist rather than leg 1 continuing

Leg 1 reached **~220,000 absolute tokens against a 150,000 hard cap** — 47% over —
having read only the artifacts this wave is about. It recommended a fresh leg
rather than pushing the implement/review/integrate cycle through that context,
which would have been the exact "push through the trip" failure the governor exists
to prevent, while writing the fix for the governor. That recommendation was
correct and is why you are here.

The same applies to you. Hand off at a gate boundary with a digest when you have
genuinely spent your context — and not before. Arriving over the band on turn one
is normal and is not a reason to stop; attach the refresh-request against the
current why-record, `start`, and work.

## Return shape

As the frozen order specifies, plus one addition: state explicitly, per ruling
R1–R5, what you implemented and what you did not, so the Admiral can tell an
accepted limit from a missed requirement.

Park at `archive`. Do not merge — publication is the Admiral's class.
