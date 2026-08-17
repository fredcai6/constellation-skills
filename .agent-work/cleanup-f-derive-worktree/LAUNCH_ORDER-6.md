# Launch Order 6: `cleanup-f-derive-worktree — #609` (leg 6 — terminal)

**Short leg. Bookkeeping only.** Your lane's code is published. Read
`ADMIRAL_RULING-5.md` first — it answers `FLOAT_TO_ADMIRAL-4.md` and carries the
waive you were missing.

## What changed since you parked

**I ran the merge gate and published.** `cleanup/f-derive-worktree` went into
`main` as a **fast-forward** at `f367cb7d`, pushed to `origin/main`. Gate arms:
`main` at `17c2cee5` → **3171 / 7 / 0**, merged `main` → **3191 / 6 / 0**,
`__pycache__` cleared before each, spine variables scrubbed, failure set empty
both ways.

## The sequence

1. **Re-claim** as `commander-cleanup-f-derive-worktree`. **Never `--force`.**
2. **Waive `c2` and `c2b`** with the reason recorded verbatim in
   `ADMIRAL_RULING-5.md`. Waived by me, on my authority — say so in the waive.
   **Waive nothing else.**
3. **`git mv` the work area** to `.agent-work/archive/2026-08-17-cleanup-f-derive-worktree/`.
   You noted the hazard yourself and you were right: `spine.json` lives inside
   that directory, so the move comes **after** the spine is terminal, not before.
   Sequence it as: close `archive`, then move, then release — or move last of all
   if your engine's terminal check reads the spine at its original path. **State
   in your return which order you used and why**, because #574 is designing this
   verb and your sequence is evidence for it.
4. **`advance archive`.**
5. **`release`** — last journaled action, as you said.
6. Commit. **Do not merge and do not push**; I take it from your branch.

## Two things to finish in your return

- **Account for the one-test discrepancy** if it is cheap: you measured 3192 / 5
  and merged `main` measures 3191 / 6. One test moved from passed to skipped.
  Failure set empty both ways, so it held nothing up. If it costs more than a
  look, say "unaccounted" and stop — do not spend a crew on it.
- **Your `feedback` gate is complete and I am not reopening it**, but if the
  reconcile-scoping finding is not in it yet, add it: *scoping a prose repair by
  file list is what let three stale claims survive; grep the claim family, not the
  file list.*

## After you

Nothing. This is the last leg on lane F. Park terminal, released, and archived,
and the lane is done.
