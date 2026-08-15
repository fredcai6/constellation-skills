## Current planning truth - epic 568, boundary wave-1-launch

**Intent.** Every piece of engine state carries who it belongs to and dies when its owner does. This run builds the ownership substrate that the deferred consumer packages read from. The outcome that must not be violated: the engine stays drivable throughout, because this epic edits the machinery every Commander in it is driving.

**In scope this tranche.** WP1 lease lifecycle (552, 383, 357, 369, 318, 330, 208), WP2 binding store (441), WP5 postcondition cwd (315), plus 530 and 510.

**Deferred, not dropped.** WP3 stop-rail attribution beyond 530, WP4 gauge and governor beyond 510, WP6 crew dispatch and liveness, WP7 pre-clearance and CLI hardening. Each reads from the substrate this tranche builds, which is why they wait rather than run alongside.

**Execution shape.** Two lanes. Engine-core files - `checklist_engine.py`, `spine_rail.py`, `agent_work_root.py` - are edited by one Commander at a time. Everything else fans out 3-4 wide.

**Current wave.** Issue 315 alone: thread `cwd=` into the command-kind check and repair the relative-check fallout across the shipped template corpus. It goes first because fixing it later would mean every gate verified before it was verified under a check that cannot fail. Its Commander enumerates the blast radius by command and states the count; the issue title's claim of five is a number to re-measure, not to inherit.

**Forecast, nonbinding.** Lease lifecycle, then binding-store durability, with 530 and 510 riding the parallel lane. None of this is a launch queue - the latitude contract expires when wave 1 merges, and the next cut is authored from wave 1's evidence.

**Open uncertainties.** How many templates actually carry a relative command check. Which spine set the 552 backfill must clear - the issue says 43 on disk, measurement says 24 active of 91 tracked. Whether a stale active lease on an archived spine blocks anything or is inert. Whether the classifier vetoes `git worktree add`.
