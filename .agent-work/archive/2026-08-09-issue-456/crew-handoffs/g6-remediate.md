# Implementer Handoff — g6 remediation

## Gate
`g6` — stale-tag detector (issue #456). This is a **rework pass on a BLOCK**, not a new build. The feature works; its evidence does not.

## Survey / plan state
Create your plan at `.agent-work/issue-456/g6-remediate/plan.json` — under the issue workbench, never at the worktree root.

## Why you are here

The `g6` reviewer returned BLOCK on one finding, and it reproduced the defect rather than asserting it. Read `.agent-work/issue-456/crew-handoffs/g6-review-RESULT.md` in full before starting.

The finding: **most of the shipped "does not flag" tests are vacuous.** The reviewer forced `stale = []` after the real computation in `extract.run()` — disabling the whole feature on one code path — reran the closing selector, and **9 of 12 tests stayed green**, including *every* dedicated does-not-flag test:

- `test_stale_tag_first_extraction_flags_nothing`
- `test_stale_tag_does_not_flag_a_reformat_across_two_extractions`
- `test_stale_tag_does_not_flag_an_unrelated_anchor`
- `test_stale_tag_render_report_does_not_flag_a_reformat`
- `test_stale_tag_render_report_does_not_fail_the_build`

Only the two "flags a real change" tests went red, plus one incidentally via its own precondition. The reviewer reverted the mutation and confirmed 12/12 and a clean tree afterwards.

This is the defect class this run has hit twice already: **a check that cannot fail carries no information.** A future change that silently disables the detector would ship green against most of its own regression suite. The feature itself is fine — independently confirmed under two separate attacks, including eight novel mutations the original crew did not choose, all of which behaved as predicted.

## Task — three fixes, one pass

### 1. THE BLOCKER: give every negative test a positive control

Each "does not flag" test must contain, **in the same test method**, an assertion that a known-should-flag mutation **does** flag. Same fixture, same build path, same assertion mechanism — so that a whole-feature disable cannot leave the method green.

The shape the reviewer prescribed: assert the target case does not flag **and** assert a control case does, in one method. Do not satisfy this by adding separate new positive tests elsewhere — a sibling test going red does not stop *this* method from lying about what it verifies.

**Acceptance is mechanical and you must run it yourself.** Reproduce the reviewer's attack: force `stale = []` after the real computation in `extract.run()`, run the closing selector, and record the count. Every one of the five methods above must go **red**. Then revert the mutation, confirm `git status --porcelain -- scripts/code_map/extract.py` is clean, and confirm the selector is green again. Report both counts — before-fix (9 green under disable) and after-fix — in your result document. If any negative test still survives the disable, you are not done; say which and why rather than declaring success.

Do the same disable-attack sanity pass on any new test you add. A positive control that itself cannot fail solves nothing.

### 2. Guard the read-before-overwrite (filed as `tc7`)

A truncated or malformed leftover `statements.jsonl` makes every subsequent `extract` die on an uncaught `JSONDecodeError` with a bare traceback naming no next step. The reviewer reproduced this.

It is a **new failure mode `g6` introduces** — before `g6` nothing read the previous store, so a corrupted leftover was harmless. And it is a real scenario, not a hypothetical: the writer has no atomic rename, so an interrupted build leaves exactly this state, and the user's natural next action is to run `build` again, which is the run that dies.

Fix: catch the parse failure at the read, treat the previous store as absent (the same path a first-ever run takes), and print one actionable line saying the previous store was unreadable and staleness comparison is skipped for this run. Do **not** silently swallow it — a silent skip turns a corrupt store into permanently-disabled staleness detection with no signal, which is the same disease in a different organ.

Cover it with a test whose name contains `stale_tag` so the closing selector catches it, and make sure that test would go red without the guard.

### 3. Rename the advisory prefix (filed as `tc8`)

The advisory line prints the literal `FAIL` while exiting 0, colliding with the prefix `checks.py` and `render.py` already use for genuine build-failing defects. One `build` invocation's stdout can carry both, distinguishable only by exit code — which humans skimming output and CI greps both routinely ignore.

Change it to `ADVISORY stale tag [...]` (or an equally unambiguous non-`FAIL` prefix). Keep the human-action wording that already ships in the message. Pin it with a test that asserts the advisory line does **not** begin with `FAIL` — name it so `stale_tag` catches it.

### 4. Nit while you are in there

The code comment citing "`gb`'s ruling" is looser than it reads: `gb`'s scope was the four ratio-based thresholds, not a ruling about advisory-versus-build-failing severity for this class of check. The underlying reasoning is sound and consistent with `gb`'s ratio-over-count philosophy; only the citation's precision needs tightening. One-line wording fix, not a redesign.

## Explicitly NOT in this pass

- **Do not change the severity ruling.** Advisory-only stands — the reviewer examined it and affirmed it. Only the *text* was wrong.
- **Do not narrow the rename sensitivity.** A bare local-variable rename tripping the flag is deliberate and was independently affirmed: "over-flag, never under-flag" is this mechanism's consistent posture. Leave it.
- **Do not build a routine exerciser for the staleness path.** The reviewer correctly established that `check` never calls `render.py` and `deterministic-rebuild` structurally cannot reach the path, so nothing automated runs it today. That is filed as `tc9` and is a design question about what `check` is for — a decision above this pass, not a defect in what you built.
- **Do not split `extract.run()`.** The Fowler pass flagged it as long (~54 → ~86 lines) and the flag is non-blocking; a split is future work if a fourth concern lands. Your guard in fix 2 will add a little more — that is accepted, do not refactor around it.
- The `NamedTuple` suggestion for the `anchor_hashes` 5-tuple is likewise non-blocking future work. Skip it.

## Allowed scope
`scripts/code_map/extract.py`, `scripts/code_map/render.py`, `tests/test_code_map.py`. Nothing else.

## Specific exclusions — flag if you need to touch them
`is_test_module`, `SPLIT_LEGEND`, `entity_symbol_join`, `page_location_matches_content`, the collision fixture, the named MUTATION fixtures, page headers, and `scripts/code_map/thresholds.py`. All were verified untouched by the original build and by the reviewer; keep it that way.

## Constraints
- The **full suite** must be green at this gate boundary (critic F6). It takes ~8 minutes — run it in the background and poll, do not block.
- The run report carries **no timings**. `stale_tags` stays a plain list of ids.
- Page headers carry path and `, N lines` — never `:<line>`. Standing human ruling.
- Every new test's method name must contain `stale_tag`, because that is the selector that closes this gate. A test the closing selector cannot see does not exist as far as this gate is concerned.

## Required evidence
1. Closing selector `python -m pytest tests/test_code_map.py -k 'stale_tag' -q --color=no` — collected/passed count, before and after your changes. Current shipped state: 12/12.
2. **The disable-attack counts**, before and after fix 1 — this is the evidence the whole pass exists to produce. Before: 9 of 12 green under disable. After: report the number and name any survivor.
3. Full suite: `python -m pytest tests/ -q --color=no`. Current baseline **1805 passed, 2 skipped, 683 subtests, 0 failed**.
4. Fresh `python -m scripts.code_map build --root .` then `python -m scripts.code_map check --root .`, in that order — `check` reads a stale tree otherwise. Current: 7/7, exit 0.
5. `git status --porcelain` clean at the end, with your work **committed** using explicit paths.

## Operating constraints, all real
- Worktree isolation REFUSES compound Bash: no loops, no heredocs, no `$(...)`, no `env -u`, no variable-assignment chaining, no long quoted strings. Use plain separate commands or a small script file. For long commit messages use `git commit -F <file>`. For long engine `--why`/`--note` values, write the text to a file and call the engine from a tiny Python wrapper passing an argv list — the previous reviewer found this route and it works cleanly.
- **Do NOT `git add -A`.** An untracked `map/` tree of ~3,930 generated pages lives here and is staged deliberately at the final gate. Explicit paths only.
- **Do not push, merge, or force-push.** Commit your own work; that is expected.
- `C:\Programs\f1Brainz` and `C:\Programs\superCoolSpaceSim` are READ-ONLY.
- Engine CLI shape: `--file` BEFORE the verb, `--session-id` AFTER. `advance` needs a positional id AND `--why`, and the item must be `in-progress` — `start <id>` first. `amend --delta`'s op key is `"op"`, not `"kind"`.
- The context governor's HARD band fires early, around 15–20% fill, often before you have written anything. It refuses `advance` until you attach `--type refresh-request --field seam=<item> --field why_ref=<latest why_trail[-1].id>`. Read that id fresh every time; every `advance` mints a new one. Comply and keep moving.

## Authority
Commit in this worktree: yes. Push, PR, merge: no — the Commander owns those. Escalating a question upward is always legitimate; if this handoff is wrong about something, say so. Crews on this run have caught eight Commander errors so far; that is the standard, not the exception.

## Return format
Return `IMPLEMENTER_RESULT` at `.agent-work/issue-456/crew-handoffs/g6-remediate-RESULT.md`: what shipped, scope touched, the evidence above with real numbers, assumptions, stop conditions, out-of-scope observations, and workflow feedback. State plainly if any part of the acceptance in fix 1 did not fully land — a partial fix reported honestly is worth far more than a clean-looking claim.

## Suggested model tier
`sonnet`.
