# Implementer Handoff: `w2-reindex-repair` — make the e2e proof survive being committed

You are implementing one bounded repair. Everything you need is below; do not go looking for wider
context.

## Task

**`tests/test_code_map_precommit_e2e.py` has six tests that only pass while the code under test is
uncommitted. Make them work from committed state.**

## The defect, precisely

`_snapshot_gates_1_2_onto()` at `tests/test_code_map_precommit_e2e.py:126` says so in its own
docstring:

> Copy gates 1-2's current **(uncommitted)** shipped code from THIS actual repo onto `worktree` and
> commit it as a baseline, so a scratch checkout can actually install and run the mechanism gates 1-2
> already shipped.

It calls `_gates_1_2_changed_paths()` to find the files, copies them into a scratch worktree, then:

```python
_git(["add", "-A", "--",
      "scripts/code_map", "scripts/hooks", "scripts/install_constellation.py"], worktree)
_git(["commit", "-q", "-m", "baseline: snapshot gates 1-2 shipped code for e2e proof"], worktree)
```

Once the lane's own work is **committed**, that `git commit` gets `nothing to commit, working tree
clean`, returns rc=1, and `_git(..., check=True)` raises:

```
RuntimeError: git commit -q -m baseline: snapshot gates 1-2 shipped code for e2e proof failed (rc=1)
STDOUT:
Not currently on any branch.
nothing to commit, working tree clean
```

Every test that calls the helper dies there.

## Reproduce it first

From `/home/tommy/projects/569-w2-reindex` (the tree is committed, so the bug is live):

```
python3 -m pytest tests/test_code_map_precommit_e2e.py -q
```

Expect **6 failed, 1 passed**: cases 2/3, 4, 5, 6, 7, 8. Case 1 passes because it deliberately never
calls the helper — it proves the pre-existing backstop's behaviour before the mechanism exists.

Confirm that before changing anything. If you cannot reproduce it, stop and say so.

## Why this matters more than its size

These six tests are the *entire* proof that the pre-commit hook behaves correctly in the cases that
actually matter — both partial-commit shapes (`git commit <pathspec>` and hunk-restricted
`git commit -p`), an unrelated dirty file surviving untouched, and a second worktree sharing the
installed hook. Those are the sharpest hazards in the whole design: a pre-commit hook that stages
files silently is only safe if it *cannot* sweep in work the author did not intend to commit.

Right now that proof is green only in the exact transient state that shipping destroys. It cannot
pass in CI, in a fresh clone, or for any reviewer who checks out the branch. This is the defect
family epic 569 exists to kill — a check whose result is true about a state that no longer exists —
so fixing it properly matters more than its line count suggests.

## What to do

Make the fixture build its baseline from **committed** content rather than from uncommitted working-tree
diff. The scratch worktree already gets the repo's committed state; the helper needs to stop assuming
there is an uncommitted delta to snapshot.

Shape is yours. Two obvious routes, neither mandated:

- Read the files from `ROOT` unconditionally (they exist either way) and make the baseline commit
  tolerate "nothing to commit" — e.g. `--allow-empty`, or skip the commit when `git status --porcelain`
  is clean, since the scratch checkout may already carry identical content.
- Derive the snapshot from `git show HEAD:<path>` rather than the working tree, so the fixture is
  explicitly about committed content.

**Requirements:**

1. All 7 tests in `tests/test_code_map_precommit_e2e.py` pass **from a clean, fully committed tree.**
2. They must still genuinely exercise the hook. Do not make a test pass by skipping it, by relaxing
   an assertion, or by making the fixture a no-op. If a case cannot be made to work from committed
   state, say which and why rather than hollowing it out.
3. **Prove it survives commitment**: after your fix, commit your change, then re-run the suite from the
   committed tree and confirm still green. That sequence — commit, then re-run — is the exact step
   whose absence caused this.
4. Do not touch `tests/test_code_map.py`'s `MapTreeFreshnessTests`. It is the backstop this whole lane
   depends on and it is fenced.
5. Do not change the hook's behaviour, `scripts/install_constellation.py`'s install wiring, or
   `scripts/hooks/code_map_precommit.py`. The mechanism is reviewed and accepted; only its proof is broken.

## Scope

**In scope:** `tests/test_code_map_precommit_e2e.py` only.

**Out of scope, do not touch:** the hook, the installer, `code_map` build code, `MapTreeFreshnessTests`,
anything under `skills/`, anything under `.agent-work/`.

If your fix appears to require changing anything outside that one test file, stop and report why —
that would mean the mechanism itself has a problem, which is a different finding and belongs to the
Admiral.

## Workspace

- **Worktree:** `/home/tommy/projects/569-w2-reindex` (branch `epic-569/w2-reindex`, PR #657 OPEN)
- Work directly on that branch and push when green; the PR updates itself.
- Do **not** merge, and do not resolve the `map/INDEX.md` conflict against `main` — the Admiral owns
  integration and will handle it.

## Return status

Report: whether you reproduced the failure first; what you changed and why that route; the full
`tests/test_code_map_precommit_e2e.py` result from a **committed** tree; the full local suite result;
and the commit SHA you verified against. If any case could not be made to work from committed state,
name it explicitly rather than leaving it skipped or weakened.
