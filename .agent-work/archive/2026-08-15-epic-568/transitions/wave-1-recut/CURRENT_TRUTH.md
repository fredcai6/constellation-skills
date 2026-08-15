## Current planning truth - epic 568, boundary wave-1-recut

**Intent.** Every piece of engine state carries who it belongs to and dies when its owner does. Wave 1 sharpened it: state that does not know **where it lives** fails the same way as state that does not know **whose it is**, and a check that asks a subprocess where it is standing can be told anything.

**Current wave.** A spine records its own repo reference at creation, and the engine enforces isolation natively against it. `init_work_area.py` stamps `origin.worktree` from the root it already computes and discards; `checklist_engine.py` compares its own `Path.cwd()` to that value at verb entry and falls back to inherited cwd when a spine has none; `init.c0`'s command check is deleted. One change, both halves, about 40 lines.

**Why not the obvious version.** Passing the stored root to the check as `cwd` reproduces the defect exactly -- the stored value and the check's expected value are the same string. That is demonstrated, not argued.

**Landed.** The regression guard, `main` at `9bb8c1b6`. It goes red against the half-built shape, so it is the wave's own tripwire.

**In scope this tranche.** WP1 lease lifecycle (552, 383, 357, 369, 318, 330, 208), WP2 binding store (441), WP5 (315, as re-cut), plus 530 and 510. Deferred: WP3 beyond 530, WP4 beyond 510, WP6, WP7.

**Execution shape.** Engine-core files edited one Commander at a time; everything else 3-4 wide.

**Merge gate, amended.** No new failures against the `main` baseline, plus an independent reviewer APPROVE, for as long as `main` is red. It lapses when `main` goes green.

**Forecast, nonbinding.** Lease lifecycle, then binding-store durability, with 530 and 510 on the parallel lane. Not a launch queue: the contract is refreshed when wave 1 merges.
