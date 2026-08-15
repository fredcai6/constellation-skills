# Plan Alternatives — tc6-doctrine

Docs-only, bounded, three named tasks from a frozen launch order; no architecture-touching interface, no
crew dispatch (the file-ownership scope IS the plan, so there is little genuine plan-space to vary). Per
`references/global-orchestrator.md` "Design-it-twice" this still runs at reduced weight (two candidates,
compared, single independent critic) rather than a skip, because the ownership/sequencing choice below is
real and worth forcing explicit.

## Candidate A — one reasoning gate per launch-order task, plus a verification gate

- `g1` — fix `docs/CHECKLIST_SCHEMA.md` (Task 1)
- `g2` — Task 2 judgment call on `skills/admiral/templates/LAUNCH_ORDER.template.md`
- `g3` — Task 3: measure `skills/workbench/references/checklist-engine.md`, sweep `docs/` + `skills/`,
  fix or record findings
- `g4` — full clean-env suite, map regeneration, evidence roll-up

**Depth**: each gate closes one launch-order task with its own close criteria — a reviewer (or the
Admiral, reading the return shape) can check each task off independently.
**Locality**: a rework of Task 2's judgment call reopens only `g2`, not the schema fix or the sweep.
**Testability**: each gate's postconditions are the specific quoted-before/after and `file:line` evidence
the launch order demands — falsifiable per task.

## Candidate B — one combined reasoning gate for all three edits, then verify

- `g1` — all three tasks' edits authored together (single pass over the doctrine)
- `g2` — full clean-env suite, map regeneration, evidence roll-up

**Depth**: fewer gates, less engine ceremony for a small run.
**Locality**: a rework of the Task 2 judgment call reopens the whole combined gate, including the already
-correct Task 1 and Task 3 work, and reopen cascades downstream (the verify gate) even though nothing
there needs redoing.
**Testability**: harder to point a reviewer at "Task 2's evidence" in isolation inside one gate's
evidence blob.

## Comparison

| axis | A | B |
|---|---|---|
| depth | 1:1 task:gate, matches launch order's own numbering | flatter, less ceremony |
| locality | rework isolated per task | rework of one task cascades the reopen through all three |
| testability | each task's before/after independently checkable | bundled, harder to audit per-task |

## Recommendation

**Candidate A.** The launch order numbers three tasks with distinct judgment shapes (a mechanical fix, a
defended either/or call, and an honest-null measurement) and an explicit File Ownership section that
already partitions the work by file. Matching gates to that partition costs one extra reasoning gate and
buys per-task locality and reviewability — worth it given Task 2 is the one most likely to need rework if
the reasoning doesn't hold up. Untaken: a per-file-in-the-sweep gate (one gate per stale surface found in
Task 3) — rejected because the sweep's own count is not known until it runs; splitting ahead of that
count would be premature structure, so Task 3 stays one gate that records what it finds.

## Panel-vs-single

Single independent critic, not a panel — this plan does not spawn epics or touch architecture (the
weight-scaling rule in `references/global-orchestrator.md`).
