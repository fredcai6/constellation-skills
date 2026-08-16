# Launch Order 3: `cleanup-b-context-identity` (relaunch, leg 3)

You are the **third leg** of this lane. Leg 2 stopped at a clean gate boundary
with its context genuinely spent, having shipped #600 — that is the handoff
working as designed, not a failure.

## Read these, in this order

1. **`STATE_NOTE.md`** — the crash-resume note. It names your next command, the
   expected artifact, what is still owed, and what must not be redone. It is
   accurate; trust it.
2. **`ADMIRAL_RULING-2.md`** — new. It accepts leg 2's R4 departure and says why
   my own R4 was wrong on that branch, and it lists what remains in priority order.
3. **`ADMIRAL_RULING-1.md`** — R1–R5, still governing.
4. **`LEG2_DIGEST.md`** — leg 2's verdict, the ruling-compliance table, and the
   three triage candidates.
5. `LAUNCH_ORDER-2.md`, then `LAUNCH_ORDER.md` — everything in them still binds
   except where the rulings amend them.

## Where you pick up

`execute` is **blocked**, deliberately, with a `refresh-request` already attached
(`e-g1-review-1`, seam `g1-review`, `why_ref w-3`) — so the guard takes its release
path for you. `g1-implement` is closed and committed at `3bc87e93`; **the g1
implementer must not be rerun.**

Re-claim the lease as `commander-cleanup-b-context-identity` and **never pass
`--force`** — the lease is yours, and #601 re-stamps `claimed_at` on a re-claim, so
you will not inherit leg 2's reading. `--force` is a takeover of someone else's
lease and does not apply here.

## What changed on `main` under you

- `df6f951b` — lane C merged: #599 and #549. Your re-measurement obligation is in
  `ADMIRAL_NOTE-lane-C-landed.md`.
- `43c577d4` — lane D: a stale-`__pycache__` guard, the `--here` message, and
  default-worktree-layout coverage.

Your branch is based on `a69bbac4`. Merge or rebase `main` before your gate, clear
`__pycache__` before every measurement, and **re-measure the baseline at gate
time** — 3057 is three commits stale, and the current `main` figure is 3089 passed
/ 7 skipped / 0 failed.

## The one thing to get right

Two legs have now ended at a context boundary. That is fine. What is not fine is
running long to avoid a third handoff: if `#500` does not fit, hand `DESIGN_500.md`
back again and say so at the boundary. An accepted limit reported plainly is worth
more to me than a rushed implementation of a design that is already settled.

Park at `archive`. Do not merge — publication is the Admiral's class.
