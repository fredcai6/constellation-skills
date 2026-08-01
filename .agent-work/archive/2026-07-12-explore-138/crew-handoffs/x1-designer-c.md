# x1 designer C — constraint: conductor inversion (the engine owns the loop)

Read `.agent-work/explore-138/crew-handoffs/x1-shared-core.md` FIRST — it holds the question, ground
truth, hard constraints, and deliverable shape. This file only assigns your constraint and result path.

## Your named constraint

**Conductor inversion.** The engine (a conductor script wrapping it) owns the loop and spawns agents,
not the other way around: read `current` → dispatch a fresh step-scoped headless agent (`claude -p`)
with ONLY that step's imperative + context → verify postconditions mechanically → `advance` → repeat.
The agent can't skip a step it never owned; compaction stops mattering (fresh context per step);
wait-by-ending-turn becomes the NORMAL control flow instead of a failure.

You must confront the cold-start economics head-on (23 of 29 min measured): design WHERE the
inversion applies — e.g. conductor for ceremony/gate steps with the execute step still agent-driven,
or step batching, or a hybrid where the conductor is opt-in per spine template. A design that
quadruples wall-clock is a failed design; say what the honest-run time becomes and how you know.
Also design: how a conductor-run step asks up to the human (the delegate-is-not-a-replacement rule),
and how existing interactive/dispatched modes coexist with conductor mode. Prior art in-repo:
`scripts/run_skill_eval.py` already spawns and grades headless runs — reuse its reap-safe patterns.

## Result path (write the design doc here)

`C:/Programs/constellation-skills/.agent-work/explore-138/evidence/x1-designer-c.md`
