# Implementer Handoff — g8, test-only fix

## Gate
`g8` (issue #456). **The production code is correct. Do not change it.** Two tests are wrong.

## What the reviewer found

Verdict `BLOCK`, but a different shape from the previous two rounds: the fix in `1f2b57ab` is right — verified by direct execution against the code, not by trusting the tests. What fails is the evidence. Two mutations that reproduce a previously-BLOCKED state of the code leave the suite **fully green**.

This is the run's recurring theme landing in the worst possible place: the invariant test. An invariant test that cannot fail is worse than no test, because it reads as the strongest evidence available while guarding nothing.

## The three fixes — tests only

1. In `test_long_first_paragraph_with_blank_line_and_body`, remove the `if summary and len(summary) == 160:` gate. Assert `len(summary) == 160` **unconditionally**, so a regression that stops truncating fails loudly instead of silently skipping the assertion block.
2. In that same test **and** in Shape 4 of `test_all_shapes_preserve_complete_content`, assert the **overflow text itself** appears in `body` — e.g. the last words of the constructed first paragraph, the ones that fall past the 160-character cut. Asserting `body is not None`, or that it contains `"Args:"`, does not test the invariant: both are true when the overflow has been dropped.
3. Nothing in `scripts/code_map/` changes. If you find yourself editing production code, stop — you are fixing the wrong thing.

## Required evidence

The whole point of this pass is that the tests can fail, so prove it:

- Reproduce the reviewer's two mutations — the states that were previously BLOCKED — and confirm both now make the suite go **red**. Name which tests fail for each. If either mutation still leaves everything green, the fix is not done.
- Then revert and confirm green again.
- Selector `-k 'bom or docstring'` before and after. Currently **11**.
- **Full suite** — `python -m pytest tests/ -q --color=no`. Baseline **1838 passed, 2 skipped, 701 subtests, 0 failed**.
- Fresh `build` then `check`. Currently 7/7. (Content should not move — this is a test-only change. If pages change, something is wrong; say so.)
- Clean tree, committed with explicit paths.

## Operating constraints
- No compound Bash: no loops, heredocs, `$(...)`, `env -u`, or long quoted strings. Plain commands or a script file. `git commit -F <file>`.
- **Do NOT `git add -A`.** The `map/` tree stays untracked until the final gate.
- No push, merge, or force-push. Commit your own work.
- Revert checks: `git diff --quiet -- <path>`, never `git status --porcelain`.
- **Write `.agent-work/issue-456/crew-handoffs/g8-remediate-4-RESULT.md` before closing your plan.**
- Prefix any scratch file with `g8-` — the shared temp directory holds other crews' generically-named files.
- Engine CLI: `--file` before the verb, `--session-id` after. `start <id>` before `advance`. Governor: attach `--type refresh-request --field seam=<item> --field why_ref=<latest why_trail[-1].id>`.

## Model tier
`haiku`.

## Note
Four rounds on this gate. Rounds one to three were my specification errors, each caught by a reviewer testing against real data. This one is different and worth naming: the code is right and the proof is hollow. A conditional guard around an assertion turns a test into a coin flip that always lands heads.
