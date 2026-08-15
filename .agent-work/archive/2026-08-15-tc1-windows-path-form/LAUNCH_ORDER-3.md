# Launch Order: `tc1-windows-path-form` — attempt 3, human ruling on your block

**Issued:** 2026-08-15 by `admiral-post-568` · **Model:** sonnet · **Frozen.**
**Supersedes** `LAUNCH_ORDER-2.md`; earlier orders still bind except where corrected here.

## Your block was correct, and it has been answered

You stopped at `g1-integrate.c1` because the cache-clean suite read **3009 passed, 1 failed** instead of
the ordered **3010 / 6 / 0 / 1136**, and you refused to self-grant a waiver its `override_policy` marks
`authority: human`. That was the right call on every count, and your diagnosis was complete:

- **Diff-independent** — you stashed the fix out of the tree and got the identical failure.
- **Environment-caused** — `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT python -m pytest -q`
  reproduced the ordered baseline **exactly**: 3010 passed, 6 skipped, 0 failed, 1136 subtests.

**This was taken to the human, who ruled.** You are not being asked to trust me on the authority.

## The ruling: correct the measurement, do not waive a failure

**Do NOT waive.** A waiver would record that a real failure was accepted. That is not what happened —
nothing is failing. The suite passes; your *measurement* was taken in a contaminated environment,
because your own active spine lease exports the three `SPINE_*` vars into the shell that runs the check,
and `tests/test_mcp_identity.py::DC3InheritanceMechanismTests::test_launching_the_parent_never_touches_the_calling_processs_own_environ`
asserts those vars are absent from `os.environ`.

**Amend the check so it measures in a clean environment.**

This has direct precedent from **today**: the `crew-verdict-and-door` lane hit this identical problem and
resolved it the identical way, amending its own `execute.json` suite checks via `retext-check` rather
than waiving. It then filed the underlying defect as a triage recommendation
(`full-suite false-fails when run inside a spine-bound shell`, priority medium). Yours is the **third**
sighting today. You are not inventing a workaround; you are applying an established one.

## Mechanics

There is **no `unblock` verb — `resume` is it** (`checklist_engine.py:532`). And `retext-check` accepts a
**pending or in-progress** gate, not a blocked one, so the order matters:

1. `resume` the blocked `g1-integrate` gate in `.agent-work/tc1-windows-path-form/execute.json`, and the
   outer `execute` step in `spine.json`.
2. `retext-check` `g1-integrate.c1` so its command strips the three vars — prepend
   `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT` to the existing pytest invocation. **Change only
   the environment prefix. Do not weaken the assertion, lower the expected counts, or narrow the
   selection.** The standard stays 3010 passed / 6 skipped / 0 failed / 1136 subtests.
3. Re-run the amended check. It must now report exactly that.
4. Advance `g1-integrate`, then drive to terminal.
5. **Commit** the one-line `tests/test_spine_origin_isolation.py` fix to branch `tc1/worktree-identity`
   and **push**, so PR #588's CI re-runs.

Record in your amendment reason that this corrects a contaminated measurement, not a standard — and cite
the clean-env reproduction you already have. The spine should read honestly to someone who was not here.

## What you are NOT doing

- **Not** waiving anything.
- **Not** fixing `tests/test_mcp_identity.py`. The human considered fixing it properly in this lane and
  chose to keep #588 minimal — it is the worktree-identity ruling, and an unrelated test-isolation fix
  does not belong in that diff. The defect stays filed for a doctrine lane.
- **Not** dispatching a crew. Everything here is yours to do in this turn. You already know why: your
  process ends when your turn ends.
- **Not** merging. The Admiral merges.

## Everything else unchanged

The one-line fix in your tree — `self.foreign.as_posix()` replacing `str(self.foreign)` — is option (a),
is correct, and is already verified. `main` has moved (PR #587 merged as `6947b15e`, `run_crew.py`); it
touches nothing you own and **you should not merge it** — keeping #588's diff minimal is what makes the
Windows CI comparison clean. The predicate, its purity, `test_it_is_pure`, and the call site's git
resolution all remain out of scope.

## Stop Conditions

- The amended clean-env check does not produce exactly 3010 / 6 / 0 / 1136.
- Amending the check would require changing anything other than the environment prefix.
- `resume` will not clear the block for a reason this order has not anticipated.

## Return Shape

What `spine_status` resolved to, named explicitly; the amended check text, before and after; the
clean-env suite counts; the commit SHA; and confirmation you pushed to `tc1/worktree-identity` with #588
still unmerged.
