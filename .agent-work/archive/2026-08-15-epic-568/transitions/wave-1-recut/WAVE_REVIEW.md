## Wave review - boundary wave-1-recut

**Exit: replan.** The repair's blocking evidence is settled, so the held wave is re-cut and a launch is authorized.

**The costing caught a trap in the direction itself.** Cut the obvious way -- store the repo root, pass it to the check as `cwd` -- the new direction *is* the falsified fix. `origin.worktree` and the EXPECTED value inside the isolation check are **byte-identical**, both deriving from the same resolved root at creation. Re-run by the Admiral rather than accepted: with the launcher in the wrong worktree, `cwd=launcher's own` REFUSES and `cwd=origin.worktree` PASSES.

**What works instead is stronger than anything proposed.** With the root stored, the engine compares its **own** `Path.cwd()` against it at verb entry. The isolation check stops being a subprocess command, `init.c0`'s command check is **deleted** rather than repaired, and the result is undisarmable by a child process and runs on every verb. No schema flag, no env var, no `--from`.

**Cost:** ~40 lines. `checklist_engine.py` ~32 across 3 sites, `init_work_area.py` ~8, `spine_lifecycle.py` zero -- `build_origin` and `open_work` were already right. **Zero edits to the 17** cwd-dependent template checks. Backfill population is **2**, because 106 of the 108 origin-less spines are archived dead runs.

**One constraint is now a no-go, not a preference:** the write and read sides land together. The engine must fall back to inherited cwd for origin-less spines, so the read side alone is inert -- a change that reports green while doing nothing. The guard merged at `9bb8c1b6` goes red on exactly that shape.

**Dropped:** the dead `spine_open` door as a prerequisite. `open_work` needs a compiled spec and only 2 exist against 12 role templates; `init_work_area.py` reaches all 12 without it.

**Contract amended by the human:** the merge gate is now no-new-failures against the `main` baseline, because `main` is independently red and the original green-exit-code gate was unsatisfiable by any PR here.
