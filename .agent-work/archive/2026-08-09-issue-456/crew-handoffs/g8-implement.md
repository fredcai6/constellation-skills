# Implementer Handoff — g8

## Gate
`g8` — two code defects (issue #456). Tenth of eleven gates. **This one is mechanical.** Two small, well-specified fixes, no design calls.

## Plan state
`.agent-work/issue-456/g8-implement/plan.json` — under the issue workbench, never at the worktree root.

## Task — two defects, split out of an old grab-bag (critic F10)

### Defect 1 — BOM-prefixed files are rejected by `ast.parse`

A file beginning with a UTF-8 byte-order mark fails to parse, so it silently drops out of the map. Fix the extractor to handle it.

**The important part: this repo has ZERO BOM files.** There is nothing here that can make this check go red. A purpose-built **fixture is therefore mandatory**, not optional — without one, any test you write passes vacuously and proves nothing. `tests/fixtures/overread_corpus/` is the precedent for a fixture corpus directory in this repo; follow its shape.

Write the fixture first, watch the test fail for real, then fix. Then break the fix and confirm the test goes red again — if it does not, the fixture is not exercising the path you think it is.

### Defect 2 — D3: the wrapped-docstring render split

A docstring that wraps across lines renders incorrectly. Find the split, fix it, and assert the corrected rendering with a test.

## Explicitly NOT in this gate

The handoff-practice items from the issue's item 9 are **closeout lessons, not build work**. They belong to the run's feedback step. Do not build them here.

## Close criteria
- A BOM fixture exists and its test goes **RED without the fix**.
- A wrapped docstring renders correctly, asserted by a test.
- Closing selector `python -m pytest tests/test_code_map.py -k 'bom or docstring' -q --color=no` — **the current baseline is 4 passing**, measured by me just now on the committed tree. (An earlier planning note said 3; `g7` added a docstring test since. If you measure something other than 4, say so — do not silently adjust.) It must grow. Anything not caught by that selector is invisible to the command that closes this gate.
- Full suite green.

## Evidence discipline — three gates in a row have been blocked on this

`g5` had a selector matching zero tests. `g6` shipped negative tests that stayed green when the whole feature was disabled. `g7` shipped a staleness test that fired off the wrong mechanism entirely, passing for the wrong reason.

Every one of those was a check that could not fail, and every one was found by someone breaking the code and watching what stayed green. So: **for each test you add, break the thing it tests and confirm it goes red. Report the result with counts.** For defect 1 specifically, the whole gate hinges on it — a BOM test written against a repo with no BOM files is the purest form of this failure available.

## Allowed scope
`scripts/code_map/`, `tests/test_code_map.py`, and a new fixture directory under `tests/fixtures/`.

## Specific exclusions — flag if you must touch them
`is_test_module`, `SPLIT_LEGEND`, `entity_symbol_join`, `page_location_matches_content`, the collision fixture, the named MUTATION fixtures, page headers, `scripts/code_map/thresholds.py`, `g6`'s staleness machinery (`span_hash`, `anchor()`, the anchored diff), and `g7`'s tag machinery (`TAG_START`, `TAG_KIND_ALIAS`, `tag_check`, `tag_lines`, the tag diff).

## Constraints
- **The BOM fixture is REQUIRED** — there is no BOM file in this repo to exercise.
- The **full suite** must be green at this gate boundary (critic F6). Baseline **1831 passed, 2 skipped, 697 subtests, 0 failed**.
- Stdlib only.
- Page headers carry path and `, N lines` — never `:<line>`. Standing human ruling.
- `render_report.json` carries no timings.
- One name for one thing.

## Required evidence
1. Closing selector `-k 'bom or docstring'`, before and after. Before: **4 passing**.
2. **The red-without-the-fix proof for the BOM fixture** — the count, observed, not inferred.
3. The break-it-and-watch-it-go-red check for every test you add, with counts and any survivor named.
4. Full suite. Baseline **1831 / 2 / 697 / 0**.
5. Fresh `python -m scripts.code_map build --root .` then `python -m scripts.code_map check --root .`, in that order — `check` reads a stale tree otherwise. Current: 7/7, exit 0.
6. `git status --porcelain` clean, work **committed** with explicit paths.

## Operating constraints, all real
- Worktree isolation REFUSES compound Bash: no loops, no heredocs, no `$(...)`, no `env -u`, no variable-assignment chaining, no long quoted strings. Plain separate commands or a small script file. `git commit -F <file>` for long messages. For long engine `--why`/`--note` values, write to a file and call `checklist_engine.main([...])` from a tiny Python wrapper with an argv list.
- **Do NOT `git add -A`.** An untracked `map/` tree of ~3,975 generated pages lives here and is staged deliberately at the final gate. Explicit paths only; other crews' bookkeeping may be loose in the tree.
- **Do not push, merge, or force-push.** Commit your own work.
- Checking whether a file reverted cleanly after a deliberate break: `git diff --quiet -- <path>` or blob OIDs. **Never** `git status --porcelain` — it false-negatives here under `core.autocrlf` and fooled two scripts at `g6`.
- The full suite takes ~7–11 minutes. Background it and poll, and **report the number yourself** — one crew on this run left that field blank and stalled 20 minutes on buffered output. If you are waiting on output that never arrives, say so rather than sitting on it.
- Writing a BOM fixture: be deliberate about encoding. Write the bytes you mean (`encoding="utf-8-sig"` or explicit `﻿`), and verify on disk that the BOM is actually there before trusting any test result.
- Engine CLI: `--file` BEFORE the verb, `--session-id` AFTER. `start <id>` before `advance`. `amend --delta` uses `"op"`, not `"kind"`.
- The context governor's HARD band fires early, often before you write anything — it trips on orientation cost. Attach `--type refresh-request --field seam=<item> --field why_ref=<latest why_trail[-1].id>`, reading the id fresh each time.

## Map anchors (inbound)
- **Structural:** `scripts/code_map/` extractor; `tests/fixtures/` — the BOM fixture.
- **Capability:** derive structure from source.
- **Constraint:** stdlib-only.
- **Evidence:** extraction correctness.

## Authority
Commit in this worktree: yes. Push, PR, merge: no. Escalating upward is always legitimate. Crews on this run have caught **nine** Commander errors — if this handoff is wrong, say so plainly rather than working around it.

## Return format
`IMPLEMENTER_RESULT` at `.agent-work/issue-456/crew-handoffs/g8-implement-RESULT.md`: what shipped, scope touched, the evidence above with real numbers, assumptions, stop conditions, out-of-scope observations, workflow feedback. State plainly anything that did not fully land.

## Model tier
`haiku`. This gate is deliberately being run at a cheaper tier than the rest of this issue, which has been sonnet throughout, to find out whether a mechanical gate needs the bigger model. That is a measurement, not a judgement about the work — do the job to the same standard and tell me in your workflow feedback if anything about the brief was harder to follow than it should have been.
