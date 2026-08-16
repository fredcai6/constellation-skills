# Leg 2 digest — `cleanup-b-context-identity` (#600, #500)

Handed off at a gate boundary, not mid-gate. `g1-implement` is **closed and
committed**; `g1-review` is **not begun**. Written for the Admiral and for leg 3.

## Verdict

**#600 is shipped and unreviewed.** The measurement was accepted and not redone.
#500 has not been started; `DESIGN_500.md` still stands as the accepted hand-back
and `g2-implement-500` carries a declared ship-or-hand-back branch.

## Why leg 2 stopped here

The engine refused `start g1-review` at **17%** of a 150,000 absolute cap:

```
REFUSED: g1-review: context at 17% is at/over the hard limit, so this is not the
moment to BEGIN work here — finish and close the gate you are already in, then
request a refresh so a fresh agent starts this one.
```

That refusal is **correct** and was obeyed rather than routed around. A
`refresh-request` is attached at `g1-review` (`e-g1-review-1`, seam `g1-review`,
`why_ref w-3`). The reading it fired on is **provably this leg's own**: it was
written by the fix itself, to
`gauge-commander-cleanup-b-context-iden-88c76234484d.json`, carrying
`"owner": "commander-cleanup-b-context-iden-88c76234484d"`. Before this wave that
same trip would have been unattributable.

## What leg 2 did, per R1–R5

| Ruling | Implemented | Notes |
|---|---|---|
| **R1** filename **and** owner field; #601's comparison stays | **yes** | `gauge-<owner>.json` plus an `owner` field in the record. The timestamp comparison is present and still fires; the implementer confirmed it by test. |
| **R2** normalize, never reject | **yes** | Slug plus hash, total over slash-bearing ids, `null`, and the literal `'$SID'`. |
| **R3** leaseless keeps today's behaviour | **yes** | Leaseless reads the unowned `gauge.json` and trips as today; leased-with-no-owner-keyed-gauge returns `None`. |
| **R4** guard is about attribution | **narrowed in one branch — see below** | Two of three branches as ruled. |
| **R5** #500 ships if context allows | **not started** | Context did not allow. Hand-back stands. |

**`decision:identity-not-time` is NOT complete**, and this is stated rather than
glossed: the wave fixes the **concurrent** collision. Passing the *harness*
identity into the engine is the only route to completing it and was out of scope.

## For the Admiral — one departure from R4, carried up rather than buried

R4 says: dedupe by owner-keyed path, write **every** distinct candidate, fire the
guard only when a candidate cannot be attributed an owner at all. The implementer
built two branches as ruled and **narrowed the third**:

| candidates | owners | behaviour |
|---|---|---|
| 1 | any | write (unchanged) |
| 2+ | all one owner | write every candidate — **R4 as ruled** |
| 2+ | any with **no** owner | skip + sidecars — **R4 as ruled** |
| 2+ | **two or more distinct owners** | skip + sidecars — **departure** |

The argument: two distinct owners under **one** binding key means two agents
reached through one harness identity, and there is exactly **one** transcript to
read. Writing that record to both files agent A's fill against agent B — the
fan-out dead end tried, measured and reverted in **#202/#261**. R4's *rationale*
("the writer could not tell whose reading it held") is satisfied by owner-keying;
its literal wording did not anticipate that third branch.

**Commander's read:** the departure is sound and conservative — that branch
behaves exactly as today, so it cannot make the governor louder — but narrowing a
`settled/admiral` ruling is not the Commander's call to make quietly. It is one
condition (`len(owners) > 1`) and reverses in one line. The reviewer is asked to
adjudicate it; the Admiral decides.

## Three triage candidates, all filed in the spine

- **`tc1` — the same defect as #600, one layer up.** A `SessionStart`/stop hook
  told the dispatched crew to drive its **parent's** `execute` gate, because it
  resolves `SPINE_FILE` from an inherited environment. Acting on it needs a
  `--force` takeover of a live parent's lease and would have deadlocked the wave.
  The crew verified the refusal by command and left `spine.json` byte-identical.
- **`tc2` — a blocked Commander goes lease-stale while healthy.** `run_crew.py`
  is blocking by design and a parent waiting on a child issues no mutating verb,
  so it cannot heartbeat. Measured: 53 minutes blocked on a live crew, and the
  engine already called that lease stale. Anything judging liveness by heartbeat
  can force-claim a spine out from under a running parent.
- **`tc3` — a format sweep is not a dependency sweep.** The prescribed Wiring
  Grep for the literal `gauge.json` could not see a dependency expressed as
  `gauge_reader.py`. The full suite caught it. Uncaught, it would have shipped a
  **dark** governor in every install.

Plus **`tc6`**, filed at `plan`: `map_orient.py verify-frame` refuses
`decision:`/`constraint:`/`assumption:`/`claim:` ids whenever the map is
DEGRADED, so a frame that complies with the required template cannot pass. All 11
refusals here were decision ids while the frame's path citations resolved cleanly.
`plan.c6` is **waived on that reason**, recorded, not skipped.

## Scope departures the reviewer must adjudicate

Three files outside the handoff's Allowed Scope: `scripts/install_constellation.py`
(+ its test) and `map/INDEX.md`. Claimed justification is that the install
destination is **flat**, so a loader written only for this checkout's layout would
fail in every install — silently, into no owner. **Verify by installing and
driving the real loader**, not by reading the argument.

## Where leg 3 picks up

1. Re-claim `commander-cleanup-b-context-identity` — **no `--force`**; #601
   re-stamps `claimed_at` so you do not inherit this leg's reading.
2. `start g1-review` (the refresh-request is already attached, so the guard takes
   its release path), then dispatch the reviewer with the **already-written**
   `crew-handoffs/g1-reviewer-handoff.md`.
3. `g1-integrate` owns two jobs nobody else can do: **retire
   `measurement/probe_cross_key.py`** (post-fix it prints `VERDICT: NEITHER`,
   which misdescribes the fixed world; `measurement/demo_owner_keyed_gauge.py` is
   the replacement, and the pre-fix output must be kept as the record of the world
   it did describe), and **re-measure against lane C** — report whether #549
   landed and re-run the probe rather than assuming either way.
4. `REPLAN_INPUT.json` is **not yet written**. The execute step's own postcondition
   runs `verify_iterative_role_artifacts.py commander`, which refuses execute
   completion without it.
5. Then `g2-implement-500` — declare ship-or-hand-back at the boundary before
   starting, per the gate's c1.
6. Park at `archive`. **Do not merge** — publication is the Admiral's class.

## Housekeeping left behind

- A stray nested directory the crew created:
  `.agent-work/cleanup-b-context-identity/cleanup-b-context-identity/` (its
  `context/` and `mechanical/` packets). Harmless, but it is path doubling and
  should be swept, not committed into the archive as if it were meant.
- `--here` isolation check at leg 2 start: `worktree OK: in
  /home/tommy/projects/constellation-skills/.worktrees/cleanup-b-context-identity`,
  rc=0.

_Leg 2, `commander-cleanup-b-context-identity`, 2026-08-16._
