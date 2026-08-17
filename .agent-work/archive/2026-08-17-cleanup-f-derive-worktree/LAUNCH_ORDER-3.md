# Launch Order 3: `cleanup-f-derive-worktree — #609` (relaunch, leg 3)

Read **`ADMIRAL_RULING-2.md`** first — it answers both items of
`FLOAT_TO_ADMIRAL-2.md` and overrules one of your recommendations, with the
reasoning. Then `ADMIRAL_RULING-1.md` (R1–R3, still governing),
`FLOAT_TO_ADMIRAL-2.md`, `STATE_NOTE.md`, and the two prior orders.

## The two answers

- **N1** — filed as **#617**, with one correction: the registry clobber is
  **pre-existing**, not lane E's. The post-`launch` `save_registry` is there at
  `e36e630b`. Your restore and your commit-as-you-go habit were right; keep both.
  Do not fix `run_crew.py` here.
- **N2** — your interaction finding is accepted and it is my chain, not your
  shortfall. **Your road 3 is overruled: take road 1 and delete the engine-side
  `worktree_from_spine_path`.** Zero external call sites is a stop condition, not
  a note, and #315 re-adds the definition *with its consumer* in #610's wave.
  Keep the shared case table on the hook copy as the rule's specification.

## Sequence

Re-claim (never `--force`), `resume` the blocked `execute`, delete the engine-side
copy, run **g3** — the half that matters — then `skip` g4 (R2) and g5 (R3) with
their recorded reasons, and fix the two stale `KeyError` claims in
`scripts/hooks/spine_rail.py:1081` and `tests/test_spine_rail.py:2698` under
`reconcile`. Then reconcile, triage, review, feedback, archive.

## Two things that changed under you

`main` is at **`17c2cee5`**, baseline **3171 passed / 7 skipped / 0 failed** —
merge it and re-measure at your gate.

**A `run_crew.py` dispatch with no `--model` is now refused outright** (#611).
Name a tier explicitly on every crew you launch, or it will not start.

Park at `archive`. Do not merge — publication is mine, and nothing is queued
behind you.
