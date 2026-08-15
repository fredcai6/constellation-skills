# Triage Recommendation: `the suite should refuse a bytecode cache whose embedded root is not the current root`

## Classification

`test-infrastructure` / `measurement-integrity`

## Source checklist/artifact

`.agent-work/epic-568/transitions/wave-2-gate-refusal/REPLAN_INPUT.json`, discrepancy
`D-pycache-contamination`, dispositioned `revise_plan` with `issue_created: true`.
Incident recorded in `.agent-work/epic-568/ADMIRAL_LOG.md`, 2026-08-14.

## Structural anchor

`tests/conftest.py` (no such guard exists today); observed through
`tests/test_episode_negative_control.py::test_every_field_has_a_named_independent_source`.

## Cartographer mismatch class

None. This is a test-harness gap, not a map-vs-code divergence.

## Observations

### Observation 1

In `.worktrees/epic-568-codex-tier-routing`, that test failed with
`OSError: could not get source code` raised from `inspect.getsource(_ControlRun.expectations)`.
The test file was byte-identical to `main`, where the same test passed.

### Observation 2

The cause was `tests/__pycache__/test_episode_negative_control.cpython-312-pytest-9.1.1.pyc`
embedding the source path
`/home/tommy/projects/constellation-skills-wt/epic-568-codex-tier-routing/tests/test_episode_negative_control.py`
— the location the worktrees occupied **before** wave 1 relocated them to `.worktrees/`. That path no
longer exists, so `linecache` returned no lines and `inspect` raised. Deleting `__pycache__` made the
test pass immediately.

**Field notes**

The failure surfaced roughly 4,000 lines away from its cause, in an assertion about oracle
independence that has nothing to do with bytecode. Attribution took four separate falsifications —
reverting the lane's `run_crew.py` to `main`, deleting the lane's three episode files, moving
`.agent-work` aside, and finally inspecting the `.pyc` bytes. Each of the first three left it red,
which is the only reason the fourth was attempted. A less patient reading would have concluded the
lane's change was defective and sent a clean branch back for rework.

The blast radius is wider than one test. Any gate measured in a relocated worktree before
2026-08-14 rests on a cache that may carry dead paths, and the wave-1 relocation touched every lane.
The failure mode is silent in the direction that matters: it fabricates failures rather than hiding
them, so it costs review time rather than correctness — but it does so while looking exactly like a
real defect in the change under test.

## Desired behavior

The suite should refuse to run, with a message naming the stale cache and the fix, when it finds a
bytecode cache whose embedded source root is not the current repo root. A one-line refusal at
startup instead of an unrelated assertion failure deep in an unrelated module.

## Possible fix

A session-scoped `conftest.py` check: for a small sample of `__pycache__` entries under `tests/`,
read the embedded source path and compare its root against the current root. On mismatch, fail
collection with the exact `find . -name __pycache__ -type d -not -path './.git/*' -prune -exec rm -rf {} +`
remedy. Sampling rather than exhaustive scanning keeps it cheap; the failure mode is uniform across
the tree, so a sample is sufficient to detect it.

Alternative considered and rejected: having the suite delete stale caches itself. A test run that
silently mutates the working tree to make itself pass is worse than one that refuses and explains.

## Open questions

- Is a sample sufficient, or does a mixed-provenance cache (some entries fresh, some stale) occur in
  practice? Observed here: the same directory held one `.pyc` with the dead path and one with the
  current path.
- Should this live in `conftest.py` or in the engine's own preflight, given that agents measure gates
  far more often than humans run the suite?

## Recommended priority

**Medium.**

**Reason:** it does not threaten correctness of shipped code, but it silently corrupts the evidence
that gates depend on, and it cost a full adjudication cycle in this epic alone. The cost recurs every
time a worktree moves.

## Related artifacts

- `.agent-work/epic-568/ADMIRAL_LOG.md` — the incident entry and its four-way falsification.
- `.agent-work/epic-568/transitions/wave-2-gate-refusal/` — the replan packets that filed it.
- PR #577 / `0dd6a6eb` — the wave-1 native isolation change whose relocation caused the stale paths.

## Disposition

**recommend-and-defer**

**Detail:** `recommend-and-defer: no tracker-filing authority was exercised this run. The epic's
planning port makes no direct gh mutation, and no wave-2 latitude covers filing new issues. Hand to
Triage or file under the human's authority at closeout.`

## Issue creation authority

Not exercised. The Admiral's delegated classes cover merge-to-main and repo hygiene, not tracker
creation. This document is the durable record until someone with filing authority acts on it.
