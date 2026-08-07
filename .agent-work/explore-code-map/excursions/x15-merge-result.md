# x15 result — merging the trial fix to f1Brainz main

**Status: MERGED.** PR [#733](https://github.com/fredcai6/f1Brainz/pull/733) squash-merged as `e3d6b542`; issue #708 CLOSED; branch and trial worktree removed.

## What happened, honestly

The dispatched merge agent created the PR and then stalled without merging or writing a result; it did not answer a status ping. The orchestrator stopped it and completed the merge directly. **This was the right outcome, because the PR as the agent left it was wrong.**

## The catch the merge gate caught

The PR at first inspection was **179 files, +20,809/−7** — not the dev agent's 3 files.

Cause: the trial worktree was branched from the human's **local** `main` (`3cf79f78`), which is one unpushed commit ahead of `origin/main` (`6c3bd350`). That commit is the human's own `docs(#724): archive the explore-physics-go-forward round` — 176 files of his archive work. The PR was therefore bundling his unpushed local commit with the fix, and a squash-merge would have flattened his archive round into a bug-fix commit on main.

The dev agent's own commit was exactly as reported: 3 files, +77/−7. No scope breach by it.

## Correction applied

1. Stopped the stalled merge agent (avoid two writers on one branch).
2. `git rebase --onto origin/main 3cf79f78 map-trial-708` in the trial worktree — replays only the fix onto `origin/main`. The human's local commit is untouched and still sits on his local `main`, unpushed, exactly as before.
3. Re-ran the gating tests on the rebased branch: **7 passed in 10.27s**.
4. Reverted the test run's side effect on the tracked binary `data/f1_data_2023.db` (known f1Brainz issue: test runs dirty it).
5. `git push --force-with-lease` on the trial branch only (never main). PR then showed **+77/−7 across 3 files**.
6. Waited for CI on the rebased head: `arch-map` pass, `docs` pass, `pyright` pass.
7. `gh pr merge --squash` → `e3d6b542`. Issue #708 auto-closed.
8. Removed the trial worktree and deleted the branch.

## Judged-good evidence

- Diff scope: exactly the 3 files named in the handoff's Allowed Scope.
- Local tests: gating file 7/7 (5 pre-existing + 2 new) on the rebased branch.
- CI: all three required checks pass on the merged head.
- The change carries the first six real grammar-tagged comments (4 `Constraint:`, 1 `Rejected:`, 1 `Rationale:`).

## Carried forward

- **Handoff/process item:** a trial branch must be cut from `origin/<default>`, not from whatever the local default branch happens to point at. An unpushed human commit underneath a trial branch silently widens any PR cut from it. Worth a line in the dispatch templates.
- The merge agent's stall is a dispatch-reliability datum, not a map finding: it created the PR, then neither merged nor reported. Cause not diagnosed.
