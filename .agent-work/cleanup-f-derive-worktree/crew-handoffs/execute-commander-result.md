# Commander Result — lane F, issue #609, leg 4

## Assigned

`LAUNCH_ORDER-4.md`, the closeout leg. Resume the held lease, re-measure the
baseline, run `g3`, then skip g4/g5, reconcile, triage, review, feedback, and
park at `archive` without merging.

## Return status

`partial` — handed off at the engine's context line, exactly as the order
sanctions. **The lease is deliberately still held.**

## What this leg completed

**`g3` — the half of #609 that matters — is implemented and independently
APPROVED.** It took five reviews and four reworks. Its `APPROVE` evidence is
already attached to `g3-review`; the next leg has only to `start` and `advance`
that gate, then `g3-integrate`.

**Every review returned a genuine, measured defect. Not one was found by
reading.**

| review | found | whose |
|---|---|---|
| 1 | **B1** the implementer's differential pinned its BEFORE arm with `git rev-parse HEAD`, so it inverted into comparing the change against itself once committed · **B2** `decide_session_start` selected by dict order, not ownership · **B3** false prose survived the symbol's deletion | g3's |
| 2 | **B4** the B2 fix newly routed "can see entries, owns none" sessions into the scan-bind, whose write then defeated the Stop path's foreign-owner withholding | g3's |
| 3 | **B5** the B4 fix guarded one of the two routes leaving `spine` `None`; the other bound the session to a spine a sibling agent visibly claimed | g3's |
| 4 | **B6** the same door still *rendered* another key's gate on an ambiguous scan · **B7** `owners` is a session view and three fresh sentences called it the store | **pre-existing** |
| 5 | nothing. **APPROVE**, 0 findings, 8/8 criteria | — |

**What g3 ships.** `_foreign_worktree` deleted with both call sites.
`_entry_mid_flight_view` reads no payload — mid-flight is a property of the
spine, so every open gate visible to the session blocks. `_own_entries` is the
shared ownership comparison at both sites. `_attributed_to_another_key` guards
the bind-on-resume's **write and its render**: neither may contradict an
attribution `session_view_provenance` already holds. A path attributed to
**nobody** behaves exactly as before, so `tc1` is untouched and no fail-closed
refusal was added (`ADMIRAL_RULING-1` R2 respected).

## The finding worth more than the bugs

**This gate removed a guard that was accidentally gating a write.**
`_foreign_worktree` was a bad ownership test and deleting it was right — but
while it stood it kept a whole class of session out of `decide_session_start`'s
fall-through. Every defect after B2 was a session arriving somewhere it had never
previously reached.

**The rule I would record: when a gate removes a guard, enumerate what the guard
was incidentally preventing, not only what it was wrongly deciding.** Nobody did
that here — not the plan, not my handoffs, not the first two crews — and it cost
four cycles.

## Verification posture

I verified in my own hands rather than accepting a return, at every turn:

- B2's regression, B4's leak and B5's leak all **reproduced by me** with the
  reviewers' harnesses before I accepted any of the three BLOCKs.
- Every fix re-verified **only after I added working-tree arms with guards** —
  because **every instrument on this gate developed a shelf-life defect**. The
  implementer's differential pinned a *moving* `HEAD` (that was B1, and it
  printed 26 confirming rows); both reviewers' scratch harnesses pinned
  *superseded* commits, so re-running them unmodified showed fixed defects as
  still present. I hit that twice.
- Both failure directions look identical to a reader — rows that agree — and both
  read as confirmation. The practice that worked, arrived at independently by
  three reviewers: **build your own instrument before you run theirs, and make
  every arm print what it actually loaded.**

## Baselines, all re-measured by this leg

| tree | result |
|---|---|
| `main` at `17c2cee5`, isolated clone | **3171 passed / 7 skipped / 0 failed** |
| pre-gate `53c89ba1` | 3170 / 5 / 0 |
| g3 pass 1 · rework 1 · rework 2 · rework 3 | 3177 · 3183 · 3187 · 3190, all /5/0 |
| **g3 rework 4 `539ff636`** | **3192 passed / 5 skipped / 0 failed** |

Failure sets empty in every direction, derived mechanically. The gate's targeted
check went **0 collected (pytest exit 5)** on the empty diff → **23 passed** —
genuinely red before the work.

The `g3` handoff had carried a stale `3195` / `main@e0539903` table; I replaced it
and named the stale numbers explicitly so the crew would not read ~3170 as a
regression.

## Floated to the Admiral — `FLOAT_TO_ADMIRAL-3.md`

Three scope questions, **none blocking**. I took a reading on each and said so.

1. **I re-opened the bind-on-resume writer**, which earlier handoffs on this gate
   fenced as `tc1`. Bounded to "may not contradict an existing attribution", under
   your rule that *the change that falsifies a claim owns the repair*. I checked
   the `#202` sibling-merge contract myself first — the spine it scans up is
   attributed to nobody, so a conflict-only guard never fires there.
2. **Should the guard reach across the session boundary?** (B7) `owners` is
   session-scoped, so a cross-session attribution is invisible. I ordered the
   prose honest and did **not** widen. The fifth reviewer named this as yours.
3. **B6 was pre-existing and I ordered it fixed anyway**, because the rule this
   gate had already shipped was incomplete without it. Flagged because "we fixed a
   pre-existing defect because our own rule implied it" is how a bounded gate
   becomes a sprawling one.

## The gate's open decision — six crews converged

> Record it **closed** and retire the refinement: **selection is a binding-key
> property at every site that selects, full stop.** The fallback was never a
> counterexample to that rule — it was the one site never held to it — and now
> that its render and its write ask the same predicate, the asymmetric refinement
> has nothing left to describe.

## My own errors, recorded

- **I cited a sha I had amended away.** My review-3 handoff named `9b1a551e`,
  replaced minutes earlier by `7d12c29d`. Content identical, no number moved, and
  the third reviewer caught it, verified the diff was empty and said so plainly.
  `ADMIRAL_RULING-3` named this exact failure and I broke it in the same document
  where I relayed the rule to my crew. **Amending a commit after citing it is a
  specific way to break "cite by the string, not the line"** and deserves its own
  line in the practice.
- **B5 was a defect in the specification I handed the implementer**, not a
  deviation from it. I prescribed the `not owned` condition; it had a second door.
- **My first `main` baseline reported a false red.** I cloned to
  `/tmp/lanef-main-baseline-4`, and `MapTreeFreshnessTests` derives
  `map/INDEX.md`'s title from the checkout directory name. Cost a full suite
  re-run. **Name baseline clones `constellation-skills`.**

## Why this leg stopped

**Not blocked, and not out of work.** The engine's context governor refuses to
`start` a new gate at 19% fill and named the handoff command itself. I am between
gates at a clean boundary, so I filed the refresh-request it named
(`e-g3-review-3`, `seam=g3-review`, `why_ref=w-16`) and parked.

Per the order: *"Running long to avoid a handoff is the failure mode, not the
handoff."*

## What the next leg owes

`STATE_NOTE.md` is current and carries the detail. In order:

1. **`g3-review`** — `start`, then `advance` (APPROVE already attached), then
   **`g3-integrate`**.
2. **`skip` g4** with **R2**, **`skip` g5** with **R3**.
3. **reconcile** — three prose repairs, all this lane's debt, including **tc10**
   in `tests/test_explorer_templates.py` and `tests/test_mcp_door_engine_cwd.py`.
4. **triage** — `tc1`–`tc12` plus the candidates the g3 crews raised.
5. **review, feedback, archive.** Park at `archive`. **Do not merge** —
   publication is yours and nothing is queued behind this lane.

## Housekeeping

- **Lease held** at `commander-cleanup-f-derive-worktree`, re-claimed without
  `--force`. Not released — the run is not done.
- **`REPLAN_INPUT.json` verifies** (`verify_iterative_role_artifacts.py commander`
  passes). Leg 4 added **D12–D21**; `g3`'s completed-outcome is parked in
  `g3-outcome-pending.json` until `g3-integrate` closes, because the G2 schema
  requires completed and open issue ids to be disjoint.
- **`crew-runs.json` committed at every gate close**, per the #617 mitigation. It
  saved nothing this leg because nothing crashed, which is the point.
- **`recover_crews.py` run before every dispatch.** Ten crews, all COMPLETE; only
  this commander leg is ACTIVE.
- **`main` has not moved** — still `17c2cee5`.
- **Nine crews on this gate refused the `SPINE MID-FLIGHT` nudge** and recorded
  the refusal, exactly as instructed. None wrote to this spine.
