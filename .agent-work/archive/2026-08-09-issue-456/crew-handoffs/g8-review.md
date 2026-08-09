# Reviewer Handoff — g8

## Gate
`g8` — two code defects (issue #456). Tenth of eleven.

## Survey State Location
`.agent-work/issue-456/g8-review/review.json`. A survey has **no `reopen`** — to re-verify after consolidating: `append` a recheck item → `record` → re-`consolidate --override-reason`.

## What was implemented

**Defect 1 — BOM.** Files starting with a UTF-8 byte-order mark failed `ast.parse` and silently dropped out of the map. Fixed at the `ast.parse` call sites in `extract.py`. Fixture at `tests/fixtures/bom_corpus/` with real BOM bytes. The crew also found the **same defect in `checks.py`'s `SourceScan`** — the validator's own second parse choked on the fixture too.

**Defect 2 — D3, the wrapped-docstring split.** A summary sentence wrapped across two physical lines was **cut in half**: the first physical line became the summary, the remainder of the same sentence opened the body. Fixed with a shared `_first_paragraph` helper plus `doc_summary_of`; all three summary sites converted; no `splitlines()[0]` remains in `extract.py`. Summary now ends at the first **blank** line (PEP 257), not the first newline.

Commits: `d727ee2f` (BOM + a first, inadequate D3 attempt) and `06fbc138` (the real D3 fix). Inspect with `git show d727ee2f` and `git show 06fbc138`.

## Context you need, because it shapes the review

This gate ran at a **cheaper model tier** than the rest of the issue, deliberately, to measure whether mechanical work needs the bigger model. Two things came out of that and both are relevant to you:

1. **The first D3 attempt did not fix the defect.** It changed `split("\n")` to `splitlines()` — cosmetically consistent, functionally identical, both still cutting at the newline. The crew *told me* it had "defaulted to a defensive fix that may not address the actual defect," which is why it got caught.
2. **`D3` was never defined anywhere.** Not in `DESIGN_SPEC.md`, not in `ISSUE_456.md` — both say only "wrapped-docstring render split (D3)". I resolved it empirically and wrote the definition into the rework brief. **My definition is itself a thing to review.** If you think the intended defect was something else, say so — I inferred it from the code's behavior, not from a spec.

## Questions this review exists to answer

**1. Is my reading of D3 right?** The rework rests entirely on it. Read `doc_summary_of`/`doc_body_of`/`_first_paragraph` and decide whether "summary = first paragraph, ending at the first blank line" is the correct rule for this codebase, or whether some other reading of "render split" fits the evidence better. Check real docstrings in this repo for shapes the paragraph rule handles badly.

**2. Do the new tests have teeth?** Three gates in a row have been blocked on checks that could not fail. The crew reports it hit exactly this: its **first** wrapped-docstring test did **not** go red on revert, because `ast.get_docstring()` normalizes output — so it wrote a different one that does. Verify the *shipped* tests: revert `_first_paragraph` to a line split and confirm they go red. Name any survivor.

**3. Boundary cases.** The brief named four; confirm each is covered and each can fail: one-line docstring (body `None`); wrapped summary with **no** blank line and no body (whole thing is the summary, body `None` — the remainder must **not** leak into the body); wrapped summary + blank line + `Args:`; first paragraph over 160 chars (truncation applies **after** joining, not before).

**4. The BOM fixture.** Confirm the fixture genuinely carries BOM bytes on disk — read the bytes, don't trust the filename — and that the test goes red without the fix. This repo has zero BOM files, so a broken fixture makes the whole check vacuous.

**5. The `checks.py` find.** Was that fix complete, or are there other second-parse sites with the same blindness?

**6. Page content changed — is it right?** Summaries across the whole repo now render whole instead of clipped. Spot-check some real pages and confirm the change is an improvement everywhere, not just in the fixture. `deterministic-rebuild` still passes, which says the build is stable, not that the content is correct.

## Close criteria
- A BOM fixture exists and its test goes **RED without the fix**.
- A wrapped docstring renders correctly, asserted by a test.
- Closing selector `python -m pytest tests/test_code_map.py -k 'bom or docstring' -q --color=no` — gate baseline **4**, now **8**.
- Full suite green.

## Allowed scope
`scripts/code_map/`, `tests/test_code_map.py`, `tests/fixtures/`.

## Specific exclusions — flag if touched
`is_test_module`, `SPLIT_LEGEND`, `entity_symbol_join`, `page_location_matches_content`, the collision fixture, the named MUTATION fixtures, page headers, `thresholds.py`, `g6`'s staleness machinery, `g7`'s tag machinery.

**Do not `git add -A`** — the untracked `map/` tree is staged deliberately at the final gate. `C:\Programs\f1Brainz` and `C:\Programs\superCoolSpaceSim` are READ-ONLY.

## Constraints
Full suite green (critic F6). Stdlib only. Page headers carry path and `, N lines`, never `:<line>`. `render_report.json` carries no timings. One name for one thing.

## Evidence produced
`IMPLEMENTER_RESULT`s at `g8-implement-RESULT.md` (first attempt) and `g8-remediate-RESULT.md` (the real fix). Read both — the first one's honest self-doubt is what saved this gate.

Commander-verified independently: suite **1835 passed, 2 skipped, 697 subtests, 0 failed** (baseline 1831); selector **8** (gate baseline **4**); fresh `build` then `check` **7/7 exit 0**; tree clean. I also confirmed the fix directly — a wrapped summary now returns whole, with the body starting at `Args:`.

## Operating notes
- No compound Bash: no loops, heredocs, `$(...)`, `env -u`, or long quoted strings. Plain commands or a script file. For long engine findings, write to a file and call `checklist_engine.main([...])` with an argv list.
- Revert checks: `git diff --quiet -- <path>`, **never** `git status --porcelain` (false-negatives under `core.autocrlf`).
- The full suite takes ~11 minutes and I have already run it — spend your effort on the six questions.
- Governor: attach `--type refresh-request --field seam=<item> --field why_ref=<latest why_trail[-1].id>`, read fresh each time.

## Return format
`REVIEW_RESULT` at `.agent-work/issue-456/crew-handoffs/g8-review-RESULT.md`: verdict, per-check findings, blockers, out-of-scope observations, workflow feedback.

Crews on this run have caught **ten** Commander errors. My D3 definition is the most likely eleventh — attack it.

## Model tier
`sonnet`.
