# Result — issue #433, `r418-433` — PENDING, handed off at the `plan` seam

**Status: not complete.** The spine tripped the context governor's HARD band at the `plan` gate. A
`refresh-request` is filed and the run is idle at the seam by design. No code has been written yet; the
plan is frozen and ready to execute.

## What stopped the run

```
REFUSED: plan: context at 19% is at/over the hard limit — advancing is blocked until you
request a refresh, so work is handed off at a seam rather than lost to a runaway.
...
REFRESH REQUESTED: plan (why_ref w-3)
CONTEXT 19% (>= hard): refresh already requested for plan — hand off now; do not keep working.
```

The trip is correctly calibrated, not spurious: `gauge_reader._PROFILES` gives `claude-opus-5` a 1M
window with a 150K hard cap, i.e. `hard = 0.15`. The gauge read `fill_fraction: 0.19077` (~191K tokens).

I considered continuing. The engine permits `advance` once the request is attached, and a recorded human
ruling describes the HARD band as a speed bump rather than a wall. I did not continue, for two reasons:
the engine's own rail text is unambiguous ("hand off now; do not keep working"), and this issue is
specifically about whether the engine's projection tells agents the truth. Buying past my own governor
while fixing the engine's honesty would make every other claim in this run worth less.

## What is done and durable

| Artifact | Path (worktree `C:/Programs/constellation-skills-wt/r418-433`) |
|---|---|
| Subsumption candidate set + inventory | `.agent-work/epic-418-redux/notes-433.md` |
| Problem statement + baseline reconciliation | `.agent-work/b433-render-directives/PROBLEM_STATEMENT.md` |
| Mission frame (verify-frame `FRAME-OK`, 0 problems) | `.agent-work/b433-render-directives/MISSION_FRAME.md` |
| Design-it-twice, two candidates + convergence | `.agent-work/b433-render-directives/PLAN_ALTERNATIVES.md` |
| Cold-critic findings + dispositions | `.agent-work/b433-render-directives/CRITIC_FINDINGS.md` |
| **Frozen gate plan (3 gates)** | `.agent-work/b433-render-directives/execute.json` |
| Spine (steps init→plan closed except plan's advance) | `.agent-work/b433-render-directives/spine.json` |

Spine state: `init`, `context`, `understand` complete. `plan` in-progress, **5/7 postconditions met** —
c1, c2, c4, c5 attested and c6 (`verify-frame`) passing; c3 needs `attest plan --cond c3 --which
postconditions --evidence e-plan-1` (the `user-decision` artifact is already attached), then `advance`.

## The three findings that matter to whoever continues

**1. The launch order's baseline is wrong in a way that changes the work.** LO-433 reads as though no
completeness property exists. It does: `tests/test_checklist_engine.py:3958`, `class
TaskFieldCompleteness`, shipped by #420, with `"directives"` sitting in its `_EXCLUDED_FIELDS` at line
4004 under an explicit `KNOWN GAP` comment. The deliverable is not "write a property" — it is render the
field, un-exclude it, and fix the property's vacuity.

**2. Un-excluding `directives` alone produces a check that cannot fail.** The property's `_flatten`
handles `str`, `[str]`, and `{k: [str] | str}` — anchors' shapes. Every populated `directives` block in
the corpus is a dict of **nested** dicts, so `_flatten` yields nothing, the inner loop never runs, and the
property asserts nothing while reporting green. Its `checked_any` guard is one flag for the whole loop, so
another field yielding text covers for a field yielding none.

**3. The cold critic found a worse hole, in my own plan.** The property loops over `t.items()` — a
**hand-built fixture**. A Task field added later and forgotten in the fixture is absent from the loop,
absent from the ledger, and passes green: the identical forgetting failure the property exists to catch.
The frozen plan's g2 now asserts the fixture's key set is a superset of the engine's own canonical Task
builder (`_build_amend_task`, `checklist_engine.py:2040`). Without this, every gate in the plan could pass
with the class still open.

## Inventory result — render, do not delete

Derived by command over every JSON file in the tree carrying a `tasks` map: **2955 gates scanned, 8 carry
a populated `directives`, all dicts, 2947 null.** The 8 are three shipped spine templates (commander
`execute`, admiral `execute`, explorer `confirm`), three archived copies of the same, and two live spines
— including this run's own. Not vestigial: `tests/test_iterative_planning_doctrine.py` asserts the parsed
contract in all three templates. Deletion, which the launch order put on the table, is declined on this
evidence.

Also measured: `docs/CHECKLIST_SCHEMA.md`'s Task table declares `directives` as `[string] | null`. That
type is **drifted** — the corpus carries dicts. Both shapes must render (the existing test fixture at line
4038 is a flat list), and the doc is corrected at g3.

## Baseline

`FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests` → **1721 passed, 4 skipped, 643 subtests, exit 0**
(592.61s, real exit code captured from `$?`, not read off the summary line). This reproduces LO-433's
stated baseline exactly.

## Isolation proof

```
$ python scripts/verify_worktree_isolation.py --here C:/Programs/constellation-skills-wt/r418-433
worktree OK: in C:/Programs/constellation-skills-wt/r418-433
EXIT=0
```

## Subsumption report

Candidate set of **10** declared before the first code change (`notes-433.md`): #392, #382, #384, #372,
#292, #390, #457, #311, #345, #458. **Closed 0 of 10** — no code shipped, so nothing is retired. The
continuation should re-examine #392 and #382 specifically: both are vacuity-family findings and the
per-field ledger is the same shape of fix.

## What the continuation does

A **fresh** Commander, same job file, cold-starting from `current` alone:

1. `claim --session-id commander-b433-render-directives --claimed-by commander --worktree .` (same id, so
   it is an idempotent resume, not a takeover).
2. `attest plan --cond c3 --which postconditions --evidence e-plan-1`, then `advance plan --why "..."`.
   Advancing `plan` is what clears the pending refresh-request — the predicate matches only the active
   gate, so no evidence mutation is needed.
3. Drive `execute.json` g1 → g2 → g3, then reconcile → triage → review → feedback → archive.

**No PR is open.** The branch `epic-418/b-433-render-directives` is pushed so the work is reachable, but
there is no code to review yet and an empty PR would only invite an accidental merge. Opening it belongs
to the continuation's `archive` step.
