# Repair result — `epic-568-510`, wave-2

**Commander:** `constellation/epic-568-510/g2-repair/commander/attempt-1`
**Order:** `.agent-work/epic-568/LAUNCH_ORDER-wave2-repair-510.md` (frozen)
**Branch:** `epic-568/510-hard-advisory` · **Worktree:** `.worktrees/epic-568-510`

## Verdict: PRE-RULING 2 FIRED. Stopped and floated; not parked at `archive`.

Three of the four failures were stale expectations and are fixed. The fourth site is not a stale
expectation: **the shipped wording is itself wrong there**, for a case #510 never intended to touch.
Under pre-ruling 2 that is agent-visible behavior in the human's decision class, so I did not fix it
in the lane and did not re-pin the expectation to it. Spine `review` gate is **blocked** with the
decision recorded. Stop condition 1 of the order.

## Suite counts (cache-clean, full Linux suite)

`__pycache__` cleared immediately before every run, per pre-ruling 5.

| | result |
|---|---|
| Before (reproduced the Admiral's gate exactly) | **4 failed, 2977 passed, 7 skipped, 1130 subtests** |
| After | **1 failed, 2980 passed, 7 skipped, 1130 subtests** |
| `main` baseline at `0448275e` | 2980 passed, 7 skipped, 0 failed |

The one remaining failure is deliberate and documented in-place: it is the visible block on the
floated decision, not an unattributed red.

## What I measured

### Pre-ruling 2, checked before touching any expectation

    E.advance(cl, "g2", why="u2")
    -> EngineError: g2 is 'pending', must be in-progress to advance

`advance` on a pending gate is refused. Two of the three failing scenarios sit at **g2 — the gate the
agent is trapped in** — where the pre-change wording ("close THIS gate … `advance g2 --why`") named a
command the engine rejects. That is exactly #510's defect, and the new pending branch states the
legal sequence instead. For those two sites the wording is right and the expectations were stale:
**pre-ruling 1, fixed.**

### The third site is a different case, and there the wording is wrong

`test_live_line_is_absent_after_the_offenders_own_close_but_the_historical_line_still_names_it`
reaches the advisory at **g3** — not the gate the agent is trapped in, but the next one, reached by
the agent's own legal close. Measured output at g3:

> CONTEXT 20% (>= hard): your instruction has changed. First request a refresh with: attach g3 …;
> then begin THIS guarded gate (`start g3`); then close it … and stop. A fresh agent picks up from
> your DIGEST; **do not begin work at another gate.**

That sentence contradicts itself, and it contradicts the guard in the same engine. `_trip_hard_gate`
refuses that identical `start g3` with:

> g3: context at 20% is at/over the hard limit, so this is not the moment to BEGIN work here —
> finish and close the gate you are already in, then request a refresh **so a fresh agent starts
> this one.**

I simulated obeying the advisory literally. Attaching the refresh-request **releases** the begin, g3
goes `in-progress`, and the trip ledger ends at:

    [('g2','begin-refused'), ('g3','begin-refused'), ('g3','begin-released')]

The engine's own compliance signal marks the agent as an over-the-line offender **for doing what the
engine just told it to do.**

The defect is in `7426ffb1`, not in this repair: the `pending` branch does not distinguish "pending
gate the agent is trapped in" (#510's ruled case) from "pending gate that is merely next after the
agent's own close". The pre-change wording is **also** wrong at g3 (`advance` on a pending gate is
refused), so **neither** wording is pinnable and no expectation in the file is correct until the
wording is decided.

## What changed

One file of substance: `tests/test_checklist_engine.py`, class
`TripLedgerComplianceOnTheHardAdvisory` (an **#467** class, not #510's anchor class). It pins the
whole advisory string byte-for-byte so the base advisory cannot silently drift; that pinned prefix
was the in-progress wording while these scenarios sit at pending gates.

**Fixed (stale expectations, both at g2 — the trapped gate):**

1. `test_compliance_line_appears_on_the_hard_advisory_only_in_the_defective_world` — g2 is pending in
   both worlds (a *refused* begin does not start a gate). `_expected_hard` -> `_expected_hard_pending`.
2. `test_compliance_line_also_rides_the_already_requested_hard_advisory` — healthy half: g2 pending
   with a refresh request -> `_expected_hard_already_requested_pending`. Defective half deliberately
   unchanged: its begin is *released*, so g2 really is in-progress there.

**Not fixed, left failing on purpose:**

3. `test_live_line_is_absent_after_the_offenders_own_close_but_the_historical_line_still_names_it` —
   expectation untouched, with an in-place comment stating the contradiction, the measurement, and
   that the decision is floated. Re-pinning it either way would have been this lane deciding
   agent-visible behavior.

Added two prefix helpers matching the shipped pending branches (verified byte-identical to the code
by evaluating both and comparing with `==`, not by eye). `_expected_hard` is retained because site 3
still uses it. Every assertion in the class is still a whole-string `assertEqual`; assertion-kind
census across the repair is `assertEqual 12 -> 13`, everything else unchanged. **No test was deleted,
skipped, or loosened**, and `scripts/checklist_engine.py` is untouched by this repair.

The fourth original failure was a stale `map/INDEX.md`, regenerated mechanically per pre-ruling 4
with `python -m scripts.code_map build --root .`. **The map is fresh** — its freshness test passes.

## Independent verification

An independent falsifier re-derived all of this: confirmed no test was deleted or weakened, confirmed
the new expected strings are byte-identical to the shipped code, confirmed
`scripts/checklist_engine.py` is untouched, and confirmed that reverting only the test file to its
pre-repair state reproduces exactly the three original engine failures. It independently found the
g3 contradiction, which I then reproduced myself before acting on it.

## Commits

- `d5ed7154` repair(510): align stale #467 advisory expectations with the pending-gate wording
- `5576d719` chore(510): capture the wave-2 repair episode
- `1022be68` float(510): stop at the after-my-own-close advisory rather than pin it

## Spine

Lease taken over from the dead predecessor session (`--force`, prior session recorded), never
recreated, and **retained** for the resume. `execute` reopened (rework 1/3), cascade-resetting
reconcile/triage/review/feedback with prior evidence superseded and retained; execute, reconcile and
triage re-driven to complete. `review` is now **blocked** carrying the floated decision and its
`next_action`. Episodes `epic-568-510-001` and `-002` are committed and tracked by git.

## Decision owed by the human (via the Admiral)

What should the HARD advisory say when the active gate is pending but is **not** the gate the agent
has been working in — i.e. immediately after that agent's own legal close? A candidate that matches
`_trip_hard_gate`'s existing refusal text: suppress the pending branch in that case and say plainly
that the agent is done and a fresh agent starts this gate. Once decided, re-pin the one expectation,
re-run the cache-clean full suite, and resume `review -> feedback -> archive`. Publication (push,
PR, merge) remains the Admiral's fenced class.
