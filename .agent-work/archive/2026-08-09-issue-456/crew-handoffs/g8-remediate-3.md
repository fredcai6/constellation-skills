# Implementer Handoff — g8 remediation, third pass

## Gate
`g8` (issue #456). One change, in the function you just edited.

## What's wrong — and it's my scoping error, not yours

Last pass you fixed exactly what I asked for: the **no-blank-line** branch of `_first_paragraph` now routes its 160+ overflow into `body`. That works, verified on real pages.

But I scoped the instruction to one branch when the invariant is general. The **blank-line** branch has the same hole: when the paragraph *before* the blank line is itself longer than 160 characters, the excess is still silently dropped at the emit sites, and the body contains only the post-blank-line content — not the truncated tail of the summary.

Same defect class as the one you just fixed. Live today on **54 real docstrings** in `scripts/` alone. Confirmed on `map/scripts.checklist_engine/_rail_position.md`.

The invariant I should have stated plainly the first time, and which is the actual requirement:

> **No docstring content is ever dropped. Whatever does not fit in the summary appears in the body — in every branch, without exception.**

## The fix

Apply the same overflow-preservation you already built to the blank-line branch. When the first paragraph exceeds the limit, its tail must be prepended to whatever body content already exists, not discarded.

Same function, same shape as the fix already shipped. Do not restructure anything else.

If the two branches now do substantially the same thing, collapse them — one overflow path that both cases flow through is harder to get half-right than two that can drift. That drift is what produced both of these findings.

## Required evidence
1. `map/scripts.checklist_engine/_rail_position.md` before and after — the dropped tail present after.
2. A test for **this** case: a first paragraph over 160 characters **followed by a blank line and body content**. Assert the summary truncates, and that both the summary's tail **and** the original body are recoverable. Then revert the fix and confirm it goes red.
3. **The invariant test, if you can write one cheaply:** for a set of differently-shaped docstrings, assert that `summary + body` always contains the full original text. That is the check that would have caught both of these at once, and it is worth more than either individual case test.
4. Both earlier cases still work — the no-blank-line overflow, and the short-wrapped-summary-then-`Args:` shape that started this. Confirm all three shapes simultaneously.
5. Selector `-k 'bom or docstring'` before and after. Currently **9**.
6. **Full suite** — `python -m pytest tests/ -q --color=no`, whole directory. Baseline **1836 passed, 2 skipped, 697 subtests, 0 failed**.
7. Fresh `build` then `check`, in that order. Currently 7/7.
8. Clean tree, committed with explicit paths.

## Not in this pass
BOM is done. Paragraph-join is right. Whether a summary should truncate *at all* is a repo-wide design question filed for triage — do not decide it here, just stop the loss.

## Operating constraints
- No compound Bash: no loops, heredocs, `$(...)`, `env -u`, or long quoted strings. Plain commands or a script file. `git commit -F <file>`.
- **Do NOT `git add -A`.** The `map/` tree stays untracked until the final gate.
- No push, merge, or force-push. Commit your own work.
- Revert checks: `git diff --quiet -- <path>`, never `git status --porcelain`.
- **Write `.agent-work/issue-456/crew-handoffs/g8-remediate-3-RESULT.md` before closing your plan.**
- Name any scratch files with the gate id — the shared temp directory already holds other crews' generically-named files, and one crew nearly clobbered another's evidence this run.
- Engine CLI: `--file` before the verb, `--session-id` after. `start <id>` before `advance`. Governor: attach `--type refresh-request --field seam=<item> --field why_ref=<latest why_trail[-1].id>`.

## Model tier
`haiku`.

## Standing note
Three passes on this defect, and the pattern is consistent: each time the specification narrowed the fix too far, and each time a reviewer testing against real data found the remainder. State the invariant, not the case. If this brief still under-specifies it, say so.
