# Launch Order: `tc1-windows-path-form` — attempt 2, the fix is already in your tree

**Issued:** 2026-08-15 by `admiral-post-568` · **Model:** sonnet · **Frozen.**
**Supersedes** `LAUNCH_ORDER.md`, which still binds except where corrected here. Read it for the
diagnosis, the (a)/(b) judgment call, and the fences.

## Read this before you do anything else

**Do not dispatch a crew. Do not spawn an implementer. Do not start a background task and wait for it.**

Attempt 1 ended with:

> The implementer crew (background task `bds4xeqiq`, PID 3033423) is running the one-line
> test-assertion fix. I'll wait for its completion notification before continuing to the review gate.

**That process is gone and it left no registry entry.** More importantly: *when your turn ends, your
process exits.* There is no scheduler, no completion notification, and nothing resumes you. Waiting is
not a thing you can do. Two other Commanders made this identical mistake today, so you are not alone —
but it stops here.

Anything you need done, you do **now**, in **this** turn, **yourself**.

## The good news: the work is done

The fix is already in your working tree, uncommitted:

```python
self.assertIn(self.worktree.as_posix(), message)
self.assertIn(self.foreign.as_posix(), message)   # was str(self.foreign)
```

That is option **(a)** from the original order, and it is the option I leaned toward. It is correct:
`as_posix()` is identical to `str()` on POSIX, so Linux behavior is unchanged, and it matches what
`git rev-parse --show-toplevel` emits on Windows, which is where the failure was.

`git status` shows exactly one modified file, `tests/test_spine_origin_isolation.py`. Nothing else.

## What remains — all of it in this turn

1. **Verify** the change is what the diff above says, and nothing more. One file, one line.
2. **State the reasoning** the original order asked for: why (a) over (b), and an argument for why the
   assertion holds on **both** Windows and POSIX by construction. You cannot run Windows here — do not
   claim you did.
3. **Run the full Linux suite, cache-clean.** Clear first:
   `find . -name __pycache__ -type d -not -path './.git/*' -prune -exec rm -rf {} +`
   Expect **3010 passed, 6 skipped, 0 failed, 1136 subtests** from inside this worktree — unchanged,
   since `as_posix()` and `str()` are the same on POSIX. **If that number moves, stop and report**: this
   change cannot legitimately alter any Linux result, so a change here means something else is wrong.
4. **Commit** to branch `tc1/worktree-identity` and **push**, so PR #588's CI re-runs.
5. Drive your spine to terminal.

## One thing that changed under you

`main` moved: PR #587 merged as `6947b15e` (`run_crew.py` — the inverted archive verdict and the unbound
external door). It does not touch anything you own. **You do not need to merge main for this one-line
change**, and I would rather you did not — keeping #588's diff minimal makes the CI comparison clean. If
you believe you must, say why first.

## Unchanged

The predicate, its purity, `test_it_is_pure`, and the call site's git resolution are all out of scope.
`scripts/hooks/spine_rail.py` (PR #589 open) and `scripts/run_crew.py` are not yours. Branch
`tc1/worktree-identity` only — do not open a second PR.

## Stop Conditions

- The Linux suite count moves from 3010 / 6 / 0.
- The working-tree change is not the single-line assertion fix described above.
- You find yourself about to dispatch anything.

## Return Shape

What `spine_status` resolved to, named explicitly; (a) vs (b) reasoning and the two-platform argument;
cache-clean suite counts; the commit SHA; and confirmation you pushed to `tc1/worktree-identity`.

**You are fenced from merging.** Say plainly that the push is done and #588 is still unmerged.
