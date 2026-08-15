# Launch Order: `tc1-windows-path-form` — one Windows assertion, and the judgment behind it

**Issued:** 2026-08-15 by `admiral-post-568` · **Model:** sonnet · **Frozen.**
Read it as written. Where it is wrong, **say so and float rather than quietly working around it.**

This is a **small, precisely-scoped follow-up** to PR #588, which is otherwise green and ready to merge.
Do not widen it.

## Mission

PR #588 (`tc1/worktree-identity`, this branch) implements the 2026-08-15 worktree-identity ruling. It is
green on Linux — 3010 passed, 6 skipped, 0 failed — and its Windows CI failure set is **89 pre-existing
failures plus exactly one new one**, which is yours:

```
tests/test_spine_origin_isolation.py::RefusesAGuardedVerbFromAForeignTree::test_the_refusal_names_both_trees_on_stderr
```

The guard itself is **working correctly**. It refused, and it named both trees. Only the separator style
in the message changed.

## The diagnosis — verify it, do not take it on trust

The CI assertion error, verbatim:

```
AssertionError: 'C:\\Users\\runneradmin\\AppData\\Local\\Temp\\tmpj6pvks9z\\elsewhere' not found in
"... REFUSED: start refused: this spine belongs to the worktree
C:/Users/runneradmin/AppData/Local/Temp/tmpj6pvks9z/wt, but the engine is running in
C:/Users/runneradmin/AppData/Local/Temp/tmpj6pvks9z/elsewhere. ..."
```

The test asserts two things:

```python
self.assertIn(self.worktree.as_posix(), message)   # stored side, posix   -> still matches
self.assertIn(str(self.foreign), message)          # cwd side, NATIVE     -> no longer matches
```

Before this ruling, the cwd side came from `str(Path.cwd().resolve())` — **native** separators on
Windows. It now comes from `git rev-parse --show-toplevel`, and **git emits forward slashes on Windows**.
So the message's cwd half is posix now, and a native-form substring assertion cannot match it.

## What is NOT wrong, so you do not go looking for it

**The comparison is separator-agnostic and stays correct.** `origin_worktree_refusal` normalizes both
sides through `os.path.normcase`, which on Windows folds forward slashes to backslashes and lowercases;
on POSIX it is the identity. So `C:/…/wt` and `C:\…\WT` compare **equal**. This is a display-and-assertion
mismatch only, not an identity bug. **Do not "fix" the predicate.** Do not add normalization to the
comparison — it is already there, and the reason it is there is documented in the docstring.

Confirm this for yourself before changing anything. If the comparison turns out **not** to be
separator-agnostic on Windows, that is a far more serious finding than this ticket and you should
**stop and report** rather than proceed.

## The judgment call — this is the part worth your attention

The message is now **internally consistent**: both halves render posix on Windows. Previously it was
**mixed** — the stored side came from `init_work_area`, which stores `as_posix()`, while the cwd side was
native. Arguably the new behavior is an improvement, not a regression.

So decide, and **say which you chose and why**:

- **(a)** Update the test's cwd-side assertion to posix form, accepting the consistent-posix message.
- **(b)** Normalize the message's rendering for display so a Windows reader sees native separators on
  both halves, and keep the test asserting native form.

I lean **(a)** — the two halves agreeing matters more than either style, `as_posix()` is already the
stored convention, and (b) means formatting work in a refusal path for cosmetics. But you are closer to
it than I am. **If you pick (b), say what it costs**, and note that (b) changes what every future reader
sees while (a) changes only a test.

Whichever you choose, the property under test — **the refusal names both trees** — must survive intact.
Losing that assertion is not an acceptable way to make this green.

## You cannot run Windows here, and that is expected

This is a **Windows-only** failure; on POSIX git and the native form agree, which is why the full Linux
suite is green. You will **not** be able to reproduce it locally. Do not fabricate a local reproduction
and do not claim you observed one.

What you **can** do, and should: assert the property in a way that is provably correct on both platforms
by construction, and reason explicitly about what the assertion evaluates to on each. If you can add a
POSIX-runnable test that would have caught this class of mismatch, that is a bonus — but not at the cost
of scope.

## Pre-Rulings — settled

1. **`decision:predicate-untouched` — settled.** `origin_worktree_refusal`'s comparison logic and its
   purity are correct and out of scope. `test_it_is_pure` must stay green, unmodified.
2. **`decision:ruling-stands` — settled.** Git-derived identity compared by equality, resolved at the
   single call site, fail-closed when nothing resolves. Not reopened by this ticket.
3. **`decision:clear-caches-before-measuring` — settled.**

## File Ownership

**Yours:** `tests/test_spine_origin_isolation.py`, and — only if you choose (b) — the refusal-message
rendering inside `scripts/checklist_engine.py::origin_worktree_refusal`.

**NOT yours:** the predicate's comparison logic, its purity, the call site's git resolution,
`scripts/hooks/spine_rail.py` (PR #589 is open on it), `scripts/run_crew.py` (PR #587 is open on it),
`.mcp.json`.

## Workspace

Worktree `/home/tommy/projects/constellation-skills/.worktrees/tc1-worktree-identity`, **branch
`tc1/worktree-identity` — the existing PR #588 branch.** Your commit updates that PR; do not branch away
from it, and do not open a second PR.

Work area `.agent-work/tc1-windows-path-form/` inside the worktree. The previous lane's work area is
archived alongside it; **leave it alone.**

## The MCP door — verify before you mutate anything

Launched through the `cli` backend with `--spine`. **`spine_status` must describe
`tc1-windows-path-form`. If it resolves to anything else — especially a `f-424` demo spine — stop and
report.**

## Evidence required

- The chosen fix, with your reasoning for (a) vs (b) stated explicitly.
- An argument — not a hand-wave — for why the assertion now holds on **both** Windows and POSIX.
- `test_it_is_pure` green, unmodified.
- Full Linux suite, cache-clean. Clear first:
  `find . -name __pycache__ -type d -not -path './.git/*' -prune -exec rm -rf {} +`
  **This branch currently measures 3010 passed, 6 skipped, 0 failed, 1136 subtests** from inside this
  worktree. Note: measured from the **primary checkout** the same tree reads 7 skipped, because
  `tests/test_spine_lifecycle.py:161` skips unless the checkout sits directly inside `.worktrees`. Both
  are correct; do not treat the difference as a regression.
- Push, so #588's CI re-runs.

## Budget

One assertion. If this grows past a handful of lines, stop and report — that would mean the diagnosis
above is wrong, which is itself the finding.

## Stop Conditions

- `spine_status` does not resolve to `tc1-windows-path-form`.
- The comparison turns out not to be separator-agnostic on Windows.
- Green would require weakening "the refusal names both trees," touching the predicate's logic or purity,
  or editing a file another open PR owns.

## Return Shape

Report: what `spine_status` resolved to, **named explicitly**; (a) or (b) and why; the two-platform
argument; cache-clean suite counts; and confirmation you pushed to `tc1/worktree-identity` so #588
re-runs.

**You are fenced from merging.** The Admiral merges. Say plainly that the push is done and the PR is
still unmerged.
