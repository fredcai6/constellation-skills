# Launch Order 5: `cleanup-f-derive-worktree — #609` (leg 5 — the closeout)

**All of this lane's code is written, reviewed, and approved.** Nothing you do
should change behaviour. If your diff touches an executable line outside the
three prose repairs below, stop and float.

## Read these, in this order

1. **`STATE_NOTE.md`** — leg 4's handoff. Current and accurate. Work from it.
2. **`ADMIRAL_RULING-4.md`** — the boundary that closed `g3`, and the two
   questions it answered. It governs your `triage`.
3. `ADMIRAL_RULING-3.md`, `-2.md`, `-1.md` — R1/R2/R3 and N2 still govern the
   skips and the reconcile list.
4. `crew-handoffs/execute-commander-result.md` — leg 4's return, and the source
   of most of your `feedback`.

## Leg 4 parked; it did not fail

`run_crew.py` records `attempt-4 -> failed` because the result artifact's status
is `partial`. The status is correct and the launcher's reading of it is wrong —
that is my defect to file, not yours. **`g3` review 5 returned APPROVE with 0
findings**, and that evidence is already attached as `e-g3-review-2`.

Re-claim as `commander-cleanup-f-derive-worktree`. **Never `--force`.** The lease
is held and yours to resume; a stale heartbeat cannot block its own owner, and its
cause is named in `ADMIRAL_RULING-3.md`.

## The sequence

1. **`start g3-review`, `advance g3-review`, `advance g3-integrate`.** The
   evidence is attached. This is bookkeeping, not work.
2. **`skip g4`** with R2 as the recorded reason. **`skip g5`** with R3.
3. **`reconcile`** — three prose repairs, all this lane's own debt, all listed in
   `STATE_NOTE.md`: the door's stale `SPINE = Path(os.environ["SPINE_FILE"]).resolve()`
   contract citation, and tc10's two files. **Cite by the string to grep for.**
   Where a repaired passage contradicts the 2026-08-15 worktree-identity ruling,
   cite that ruling and say plainly that this lane supersedes it.
4. **`triage`** — `tc1`–`tc12` plus what `g3` added. Under `ADMIRAL_RULING-4`:
   `tc1` and the cross-session widening (B7) go to **#610's wave as one package**,
   carrying the *question* — what the scan-bind is for when nobody has claimed the
   spine — and not just the symptom.
5. **`review`**, **`feedback`**, **`archive`**.

## Your `feedback` is the most valuable artifact this lane will ship

Leg 4's return has the material. At minimum, record:

- **When a gate removes a guard, enumerate what the guard was incidentally
  preventing, not only what it was wrongly deciding.** Four of five g3 reviews
  trace to nobody doing this.
- **Build your own instrument before you run theirs.** Every instrument on this
  gate developed a shelf-life defect — a differential pinned to a moving `HEAD`,
  reviewer harnesses pinned to superseded commits showing fixed defects as live.
- **Cite content that cannot move under you.** Stale line numbers (mine, five
  times) and amended shas (leg 4's, once) are the same defect in two forms.
- **Measure the claim family, not the symbol.** g2 cost three implementer passes
  because every check keyed on a symbol while the defect lived in a claim wrapped
  across comment lines.

## Baselines

`main` is at **`17c2cee5`** and has not moved. Re-measure both arms at your gate
rather than citing leg 4's numbers. If you clone to measure, **name the clone
directory `constellation-skills`** — `MapTreeFreshnessTests` derives the map title
from the checkout directory name and a clone elsewhere reports a false red.

## Park

**Park at `archive`. Do not merge.** Publication is mine and nothing is queued
behind you. Handing off again at a clean gate boundary is allowed and correct if
your context is spent.
