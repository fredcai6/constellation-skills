# notes-461 — issue #461, the negative control reds every legitimate capture

Implementer-with-a-plan, wave 3 dispatch W3-B, delegated under `LO-461.md`. Worktree
`C:/Programs/wt-w3b-461`, branch `epic-418/w3b-461`.

## Isolation proof (first command, before any git operation)

```
$ python scripts/verify_worktree_isolation.py --here C:/Programs/wt-w3b-461
worktree OK: in C:/Programs/wt-w3b-461
EXIT:0
```

## The fix

`tests/test_episode_negative_control.py::test_canon_episode_store_untouched` narrowed to
worktree-vs-index only, per `decision:worktree-vs-index-only`: replaced the single
`git status --porcelain episodes/` read (which also reports index-vs-HEAD, so a staged
capture ahead of its commit reads as "dirty") with the named pair —
`git diff --name-only episodes/` (tracked-but-unstaged) plus
`git ls-files --others --exclude-standard episodes/` (untracked-and-unstaged) — asserted
separately so a failure names which half tripped. Docstring rewritten to state the
worktree-vs-index property explicitly and explain why the old predicate was wider than it.
`decision:preserve-anti-vacuity` untouched: the non-emptiness assertions above it
(`len(tracked) >= 2`, at least one `.md`) are unchanged.

Only `tests/test_episode_negative_control.py` was touched — the fenced file this wave
owns. Nothing under `episodes/` or `scripts/apply_episode_delta.py` was needed or edited;
the defect was entirely in the assertion's git-command choice.

## The three falsifications — observed against the real repo, output pasted

All three were produced by mutating the actual working tree under `episodes/active/` in
this worktree, running the single test, and reverting fully before moving to the next
case. `git status --porcelain episodes/` was empty before the first case and is empty now
(confirmed below) — no residue survived any of the three probes.

### 1. Stray unstaged write under `episodes/active/` — still FAILS

```
$ echo "stray unstaged write" >> episodes/active/b433-render-directives-001.md
$ git diff --name-only episodes/
episodes/active/b433-render-directives-001.md

$ FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_episode_negative_control.py::test_canon_episode_store_untouched
...
>       assert unstaged == "", f"canon episode store has unstaged edits: {unstaged}"
E       AssertionError: canon episode store has unstaged edits: episodes/active/b433-render-directives-001.md
E       assert 'episodes/act...ctives-001.md' == ''
E
E         + episodes/active/b433-render-directives-001.md

tests\test_episode_negative_control.py:1161: AssertionError
1 failed in 0.63s
```

Reverted: `git checkout -- episodes/active/b433-render-directives-001.md`.

### 2. Stray untracked file under `episodes/active/` — still FAILS

```
$ echo "junk" > episodes/active/stray-untracked-461.md
$ git status --porcelain episodes/
?? episodes/active/stray-untracked-461.md

$ FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_episode_negative_control.py::test_canon_episode_store_untouched
...
>       assert untracked == "", f"canon episode store has untracked files: {untracked}"
E       AssertionError: canon episode store has untracked files: episodes/active/stray-untracked-461.md
E       assert 'episodes/act...racked-461.md' == ''
E
E         + episodes/active/stray-untracked-461.md

tests\test_episode_negative_control.py:1167: AssertionError
1 failed in 0.63s
```

Reverted: `rm episodes/active/stray-untracked-461.md`.

### 3. Staged-but-uncommitted legitimate capture — PASSES

This is the exact scenario the issue is about: `write -> git add -> suite -> commit`,
observed mid-window, after `git add` and before the commit.

```
$ echo "legit episode capture body" > episodes/active/stray-untracked-461.md
$ git add episodes/active/stray-untracked-461.md
$ git status --porcelain episodes/
A  episodes/active/stray-untracked-461.md

$ FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_episode_negative_control.py::test_canon_episode_store_untouched
.                                                                        [100%]
1 passed in 0.36s
```

Reverted: `git reset episodes/active/stray-untracked-461.md && rm episodes/active/stray-untracked-461.md`.

Under the OLD predicate (`git status --porcelain`), case 3 would have printed
`A  episodes/active/stray-untracked-461.md` and failed — that `A ` line is exactly the
`canon episode store is dirty: A  episodes/active/issue-447-008.md` failure the issue
quotes from #447 g4 and the Admiral reproduced during #460's merge.

Post-probe clean check:
```
$ git status --porcelain episodes/
(empty)
```

## Full suite — real exit code

```
$ FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
1782 passed, 2 skipped, 683 subtests passed in 484.38s (0:08:04)
EXIT:0
```

Matches the wave-2 baseline pasted in the launch order (`1782 passed, 2 skipped, 683
subtests, exit 0`) exactly — no regressions, no count drift.

## Pre-rulings applied

- `decision:falsify-dont-assert` — followed; all three cases observed and pasted above,
  not merely claimed.
- `decision:worktree-vs-index-only` — used the named pair as given (`git diff
  --name-only` + `git ls-files --others --exclude-standard`), asserted as two separate
  checks rather than one combined string so a failure names which half tripped.
- `decision:docstring-and-predicate-agree` — docstring rewritten to state the
  worktree-vs-index property and name why the old predicate over-fired; the predicate
  now measures exactly what the docstring claims.
- `decision:preserve-anti-vacuity` — untouched; the non-emptiness assertions stand
  before the worktree-vs-index checks, in the same order as before.

## Triage candidates

- `tc1` — the module-level "belt and braces" comment block (around line 984) still says
  "the store's blob-OID checks" as this test's role; that phrase pre-dates this fix and
  was already slightly loose (the test reads `git ls-files -s` for the non-emptiness
  assertion, not literally "OID checks" as its main property) — left alone, out of this
  issue's scope per the launch order's explicit exclusion of "the store's blob-OID
  checks."
- `tc2` — the same class of defect the launch order names ("wider than stated intent")
  may recur anywhere else in the repo that shells out to `git status --porcelain` as a
  cleanliness gate rather than the worktree-vs-index pair; not searched for here (out of
  scope), flagged for a future sweep.

## Workflow feedback

- The falsification-first structure in the launch order worked well as a forcing
  function: writing the three throwaway repro cases before trusting the fix caught
  nothing wrong here, but the discipline of reverting fully between each case (rather
  than batching them) made it easy to confirm zero residue with a single `git status
  --porcelain episodes/` at the end.
- The full suite takes ~8 minutes; the default 2-minute Bash timeout undercounts it by a
  wide margin. Running it in the background with a longer timeout and polling worked,
  but a future launch order for this repo could save a retry by naming the expected
  wall-clock duration alongside the expected pass count.
