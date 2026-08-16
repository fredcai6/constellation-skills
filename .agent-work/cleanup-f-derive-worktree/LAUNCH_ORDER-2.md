# Launch Order 2: `cleanup-f-derive-worktree — #609` (relaunch, leg 2)

You are the second leg of this lane. Your predecessor blocked `execute` and
floated three rulings. All three are answered, and **two of them were my errors,
not yours.**

## Read these, in this order

1. **`ADMIRAL_RULING-1.md`** — the answers. It supersedes the frozen order
   wherever they disagree, and it says exactly where.
2. **`FLOAT_TO_ADMIRAL.md`** — your predecessor's three floats, all accepted as
   measured.
3. **`STATE_NOTE.md`** — where to pick up.
4. **`LAUNCH_ORDER.md`** — the original. Everything still binds except as amended.

## The three answers, in one line each

- **R1** — the widening on a leaseless spine is **accepted**. Narrow the claim in
  the four places, close `g2-integrate`. My "the lease is and always was the
  guard" was true only where a lease exists; I did not qualify it.
- **R2** — `nearest-ancestor-fail-closed` is **withdrawn and replaced**. An
  unowned spine path yields **no derived worktree and today's behaviour**, not a
  refusal. Your 362-of-429 measurement is why. Re-author `g4` to that shape.
- **R3** — **#315 leaves this lane.** `skip` `g5`. My "zero occurrences in any
  template" was measured on the shipped tree and missed the project-local overlay,
  which carries a live `c0`. It re-homes to #610.

## What remains

`g2-integrate` (resume and close), `g3` (the worktree stops answering "is this
mine" — the half of #609 that matters most), `g4` re-authored, `g5` skipped. Then
reconcile, triage, review, feedback, archive.

## Two things that changed under you

**`main` is at `e0539903`**, two merges ahead of your base: lane A (#603/#604/#605
— the door refuses when unbound, `spine_open` binds it, the demo spine is
generated) and lane E (#607/#525 — the parent heartbeats while blocked, crew
scratch is namespaced). Merge `main` before your gate and re-measure: the baseline
is **3163 passed / 7 skipped / 0 failed**, not the 3103 your predecessor's order
quoted.

**Two of your own files carry claims lane A falsified.**
`scripts/hooks/spine_rail.py:1081` and `tests/test_spine_rail.py:2698` still say
the door raises `KeyError` when `SPINE_FILE` is unset. It refuses by name now. You
own both; fix them under `reconcile` and say so.

## Lease and context

Re-claim as `commander-cleanup-f-derive-worktree`. **Never `--force`** — #601
re-stamps `claimed_at` on a re-claim, so you will not inherit leg 1's reading, and
`--force` is a takeover of someone else's lease.

Arriving over the HARD band is not a stop condition. Attach the refresh-request
against the current why-record, `start`, then work. Handing off at a clean gate
boundary when your context is genuinely spent is correct and is how four lanes
have finished today; running long to avoid it is not.

Park at `archive`. Do not merge — publication is mine. Your merge is **no longer
held**: lanes A and E are both in, and nothing is queued behind you.
