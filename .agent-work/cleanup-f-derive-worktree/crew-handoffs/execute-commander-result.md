# Commander result — `cleanup-f-derive-worktree` (#609 lane F), leg 5

## Assigned

`LAUNCH_ORDER-5.md` — the closeout. Close `g3` on the APPROVE already attached,
skip `g4` and `g5` on the recorded rulings, then reconcile → triage → review →
feedback → archive, parking at `archive` without merging.

## Return status

`partial` — **parked at `archive`, exactly where the order said to park.** Nine of
the ten spine steps are complete; `archive` is `in-progress` with its local half
done and its publication half untouched, because publication is yours. The lease
is **deliberately held** — the run is not done until you close it.

## Everything the order asked for, done

**`execute.json` is terminal.** `g3-review` advanced on review 5 — APPROVE, 0
findings, 8 of 8 criteria, no blockers — which `ADMIRAL_RULING-4` made the last
round. `g3-integrate` closed with every load-bearing number re-measured **at this
gate, by me**, not cited from leg 4:

| arm | result |
|---|---|
| `main` at `17c2cee5`, isolated clone named `constellation-skills` | **3171 / 7 / 0** |
| shipped tree at `539ff636`, engine's own quiet `c2` run | **3192 / 5 / 0** |
| targeted class `OwnershipIsBindingKeyNotWorktree` | **23 passed**; the same selector exits 5 on the pre-gate arm |

**Failure-set difference: empty against empty.** The 7→5 skip delta predates the
gate — the pre-gate arm already measured 5. Windows path handling is stated
explicitly and honestly: everything compares through `_same_path`
(`normcase` + `normpath`, `True` on exception), both call sites fold case
identically, and because `normcase` is the identity on this host the case
expectation is **constructed**, not measured.

**`g4` skipped as WITHDRAWN** (R2) — the pre-ruling it implemented was itself the
defect, and `_worktree_from_spine` returning `None` is already the whole answer,
which I verified by reading the function rather than citing g1. Nothing re-homes
from it. **`g5` skipped as RE-HOMED** (R3) — #315 stays open and moves to #610's
wave.

**`reconcile`** — six stale-claim sites repaired across five files, all prose, no
executable line moved, suite unchanged at 3192/5/0. **`triage`** — 21
recommendations, nothing unrouted, nothing filed. **`review`** — run summary
recorded, citing the order. **`feedback`** — five episodes plus the reflection.

## The two departures, both recorded rather than quiet

**1. Reconcile repaired six sites where the order named three.** Grepping the
*claim* rather than opening the named files found three more members of the same
family: `scripts/init_work_area.py`'s `instantiate_spine` docstring, `tc9`'s
`tests/test_worktree_derivation.py` docstring, and the `tests/test_spine_rail.py`
copy that was only findable by a fragment because the claim wrapped across two
comment lines. All were falsified by this lane's own `g2`, so your rule — *the
change that falsifies a claim owns the repair* — puts them here. **Scoping a
prose repair by file list is what let three of them survive.** Recorded as T22 and
`D28`. If you would rather they had gone to #610, they are three prose reverts.

**2. Two gates were begun over the context governor's line**, by the engine's own
documented sequence — request the refresh, `start` the pending active gate,
`advance --why` — and both are in the trip ledger as `begin-instructed`
(`tl-6`, `tl-8`), the outcome the compliance selectors deliberately do not count.
In both cases the gate's whole substance was done, attested and committed
**before** the gate was begun.

**I nearly parked this leg at `reconcile` on a misreading of that refusal** —
having read the refusal without reading the trip ledger under it, which already
showed refuse-then-instruct twice. The previous leg parked one gate earlier on
the same misreading. It is episode `-005`, and it is the cheapest lesson in this
lane: **`attest` and `attach` are not governor-guarded, so do the gate's substance
before you start it.**

## The one decision that is yours — `FLOAT_TO_ADMIRAL-4.md`

**`archive`'s postconditions and `LAUNCH_ORDER-5` disagree, and I did not resolve
it myself.**

- `c2` wants the branch **pushed**; `c2b` wants an **OPEN or MERGED PR**; `c3`
  wants the lease **released** after a final `advance`.
- The order says *"Park at `archive`. Do not merge. Publication is mine."*

This branch has **no upstream and no PR**. I did not push, did not open one, and
did not waive the checks to manufacture a terminal spine. **I also did not move
the work area** to `.agent-work/archive/<date>-…`: `spine.json` lives inside it,
and moving it while the spine is non-terminal would strand the next leg's
`--file` path.

Three ways to close it, all yours: authorize the push and the PR and let a leg
finish `archive`; or waive `c2`/`c2b` with the fence as the recorded reason; or
take the branch yourself and close the spine as part of publication.

## What is ready for you

- **Branch `cleanup/f-derive-worktree`, clean**, everything committed. Code
  through `684502ab`; run record through this commit. **`main` unmoved at
  `17c2cee5`**, re-measured here.
- **`TRIAGE_RECOMMENDATIONS.md`** — 21 recommendations. **T13 is your package**:
  the SessionStart scan-bind and B7's cross-session blindness routed to #610's
  wave *together*, written so the wave inherits **the question** — what the
  scan-bind is *for* when nobody has claimed the spine — not just the symptom.
  Four are `fixed-now` with shas; nineteen are `recommend-and-defer`, for the one
  stated reason that no filing authority was granted. **Read its opening warning:**
  `execute.json`'s `tc1` and the order's `tc1` are different findings with the
  same name.
- **`REPLAN_INPUT.json`** — `g1`/`g2`/`g3` as completed outcomes, open set empty,
  23 wave-evidence rows, `D0`–`D28`. `verify_iterative_role_artifacts.py commander`
  passes. Nothing auto-filed.
- **Five episodes**, tracked under `episodes/active/cleanup-f-derive-worktree-001…005`,
  proved by the archive-phase capture gate. Plus `FEEDBACK.md`.

## Three things worth your attention beyond this lane

1. **`D27` — the governor costs a closeout roughly a leg per gate** at the shipped
   0.08/0.15 defaults, since re-orientation alone eats about a tenth of a window.
   The mitigation this leg found — do the substance while the gate is still
   pending, then use the sanctioned start-and-advance — makes the tail closable in
   one leg, and it is worth writing into the Commander doctrine rather than
   rediscovering.
2. **`D22` — `run_crew.py` records a `partial` result as `failed`.** Legs 4 and 5
   both parked correctly at clean boundaries; the registry calls both failures.
3. **`T11`/`D23` — the containment test measures its observer.** Every tool call
   fires the gauge chain into the `.agent-work/` that test snapshots, so any agent
   watching its own suite run gets a red that is indistinguishable from a
   regression, at a gate whose postcondition is a green suite.

## Housekeeping

- **Lease held** at `commander-cleanup-f-derive-worktree`, re-claimed without
  `--force`, never released — the run is not done.
- **No crew dispatched this leg.** `recover_crews.py` was run before starting;
  every `g3` crew is COMPLETE and legs 1–4 are my own parked predecessors, not
  crews to recover.
- **`crew-runs.json` committed at every gate close**, per the #617 mitigation.
- **Nine crews on this issue refused the `SPINE MID-FLIGHT` nudge** and recorded
  the refusal. None wrote to this spine. The mechanism is T13.
