# Implementer Handoff — g8 remediation, second pass

## Gate
`g8` (issue #456). BOM is done and stays. **My D3 fix regressed the majority case.** This is my error, not yours.

## Plan state
`.agent-work/issue-456/g8-remediate-2/plan.json`.

## What went wrong — read this before touching anything

I defined D3 empirically because the spec never did, and I got the symptom right but the consequence wrong. The reviewer checked my definition against real docstrings in this repo, exactly as it was asked to, and found the fix makes things worse for the dominant case.

**This codebase's most common docstring shape is a single dense multi-line paragraph with no blank line at all** — 132 of them exceed 160 joined characters in `scripts/**/*.py` alone.

Under my rule, for that shape:
- the whole docstring becomes "the summary",
- it gets hard-truncated to 160 characters at the emit sites,
- `doc_body_of` returns `None`,
- so **everything past 160 characters is silently gone.** No ellipsis, no body, no signal.

Under the old pre-`g8` code, the first physical line became the summary and **the rest was preserved, untruncated, in the body.** So my fix trades a cosmetic mid-sentence split for actual content loss across a large fraction of the corpus.

Confirmed on two real regenerated pages in this worktree's `map/` tree:
- `map/scripts.agent_work_root/_git_rev_parse.md` — summary ends mid-word: `"...and lets OSError (g"`. No body. The docstring's real tail is gone.
- `map/scripts.checklist_engine/_glob_to_regex.md` — same shape, cut mid-clause, no body.

This contradicts `DESIGN_SPEC.md`'s own stated purpose for the summary (line 129): *"DO carry the structural summary that saves opening the file at all."* A summary that drops the back half of the only real content does the opposite.

## The fix

**When `_first_paragraph` finds no blank line, the overflow past the truncation limit must go into `body`, not be discarded.** That makes the no-blank-line case symmetrical with the blank-line case: nothing is ever silently lost.

Keep everything else. The paragraph-join mechanism is right — a wrapped summary sentence should still arrive whole. The BOM fix is right. Only the overflow handling changes.

Shape it however reads cleanest inside `_first_paragraph` and the emit sites' truncation logic, but the invariant to hold is: **no docstring content is ever dropped without appearing somewhere.** If you find yourself unable to hold that invariant without a bigger change, stop and say so rather than approximating it.

## Also: the missing boundary test

The brief's fourth boundary case — a first paragraph over 160 characters, truncation applying **after** joining — was never tested. The reviewer confirmed the truncation itself behaves correctly, so this is a coverage gap rather than a second bug. But it is precisely the test that would have caught this regression, **if it had been written against a real-shaped docstring (no blank line, long) rather than a short synthetic one.**

Write it that way: a realistic dense paragraph with no blank line, over 160 characters. Assert the summary is truncated **and** that the remainder is retrievable in the body. Then revert the overflow fix and confirm it goes red.

## Required evidence
1. The two real pages above, before and after — `map/scripts.agent_work_root/_git_rev_parse.md` and `map/scripts.checklist_engine/_glob_to_regex.md`. Show the tail is no longer lost. This is the evidence this pass exists to produce.
2. The new >160-char no-blank-line boundary test, and the break-it-and-watch-it-go-red result for it.
3. Closing selector `-k 'bom or docstring'` before and after. Currently **8**.
4. **The full suite** — `python -m pytest tests/ -q --color=no`, the whole `tests/` directory. Baseline **1835 passed, 2 skipped, 697 subtests, 0 failed**. Background it and poll; ~11 minutes.
5. Fresh `python -m scripts.code_map build --root .` then `python -m scripts.code_map check --root .`, in that order. Currently 7/7. Page content will change again — that is the point.
6. Clean tree, committed with explicit paths.

## Not in this pass
- BOM is done. Leave it.
- Keep the paragraph-join. Keep `_first_paragraph` as the shared helper.
- The duplicated one-line BOM-strip across three call sites is a noted, non-blocking smell. Skip it.
- Whether a summary should *ever* silently truncate is a repo-wide design question filed for triage. Do not decide it here — just stop the content loss.

## Constraints
Full suite green (critic F6). Stdlib only. Page headers carry path and `, N lines`, never `:<line>`. `render_report.json` carries no timings. One name for one thing.

## Operating constraints
- No compound Bash: no loops, heredocs, `$(...)`, `env -u`, variable-assignment chaining, or long quoted strings. Plain separate commands or a script file. `git commit -F <file>`.
- **Do NOT `git add -A`.** The untracked `map/` tree is staged deliberately at the final gate.
- Do not push, merge, or force-push. Commit your own work.
- Revert checks: `git diff --quiet -- <path>`, never `git status --porcelain`.
- **Write `.agent-work/issue-456/crew-handoffs/g8-remediate-2-RESULT.md` BEFORE closing your plan.** Third time asking — the result document is the deliverable the gate matches on, and both previous passes needed a nudge for it.
- Engine CLI: `--file` before the verb, `--session-id` after. `start <id>` before `advance`. Governor: attach `--type refresh-request --field seam=<item> --field why_ref=<latest why_trail[-1].id>`, read fresh each time.

## Model tier
`haiku`. The defect is precisely specified and the fix is scoped to one function's overflow handling.

## A note on how this gate has gone
Your first pass said the defect was underspecified and that your fix might not address it. You were right. My replacement definition was then wrong in a different way, and the reviewer caught it by testing my rule against real data instead of accepting it. That is the process working, and it is the eleventh Commander error crews have caught on this run. Say so plainly if this brief is wrong too.
