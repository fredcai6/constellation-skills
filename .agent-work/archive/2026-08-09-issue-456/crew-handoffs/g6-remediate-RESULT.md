# Implementation Result

> Write per `constellation-how-to-talk` — clear, concise, grounded, one name per thing (`docs/agents/GLOSSARY.md`).

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g6` — stale-tag detector (issue #456), rework pass on a BLOCK.

## Completed slice
All three fixes named in the handoff, plus the nit, in one pass:

1. **THE BLOCKER (fix 1):** every one of the 5 named "does not flag" tests now carries, in the same
   test method, an in-method positive control — a known-should-flag mutation asserted to actually
   flag, using the same fixture/build path/assertion mechanism already in the method. Verified
   mechanically with a script that reproduces the reviewer's disable attack, not by reasoning about it.
2. **tc7 (fix 2):** `extract.py`'s previous-store read is now guarded against a truncated/malformed
   leftover `statements.jsonl` — treated as absent (the bootstrap path), with one actionable printed
   line, not a silent skip.
3. **tc8 (fix 3):** the advisory stale-tag line's `FAIL` prefix is renamed to `ADVISORY`, removing the
   collision with `checks.py`'s/`render.py`'s own build-failing `FAIL` convention. Pinned with a test.
4. **Nit (fix 4):** the code comment citing "`gb`'s ruling" is reworded so it no longer implies `gb`
   ruled on advisory-vs-build-failing severity for this check class — `gb`'s own ruling scoped only
   its four ratio-based thresholds; the underlying twitchy-tripwire reasoning still carries over.

## Scope
**Files changed:**
- `scripts/code_map/extract.py` — read-guard around the previous-store read in `run()`
- `scripts/code_map/render.py` — `FAIL` → `ADVISORY` prefix rename; `gb` citation reworded
- `tests/test_code_map.py` — 5 existing methods rewritten with positive controls; 2 new methods added

**Specific exclusions touched:** no — `is_test_module`, `SPLIT_LEGEND`, `entity_symbol_join`,
`page_location_matches_content`, the collision fixture, the named MUTATION fixtures, page headers,
and `scripts/code_map/thresholds.py` were not touched (confirmed by review of the diff below).

## Behavior changed
Yes:
- The 5 rewritten tests now fail if the whole staleness feature is disabled on the `extract.run()`
  code path — previously they stayed green under that condition.
- `extract` no longer crashes on a truncated/malformed leftover `statements.jsonl`; it treats the
  store as absent and prints one actionable line.
- The advisory stale-tag line no longer starts with `FAIL`; it starts with `ADVISORY`. The severity
  (advisory-only, does not fail the build) is unchanged — only the text.

## Map Impact
- **Structural anchors touched:** `struct:extract.run` (scripts/code_map/extract.py) — the
  previous-store read now guarded by try/except; `struct:render.check_report_and_print` region
  (scripts/code_map/render.py, the stale-tag print loop and the return-statement comment) — prefix
  and comment text only, no logic change.
- **Capabilities added/changed/affected:** the g6 stale-tag detector's negative-test evidence is now
  load-bearing (see Behavior changed above) — this closes the exact gap the `g6` review BLOCKed on.
- **Constraints/assumptions touched:** the "advisory does not fail the build" ruling from `gb` is
  unchanged; only the citation naming it is now accurate about what `gb` actually scoped.
- **Trust limitations / drift found:** none found beyond what the reviewer already surfaced (`tc9`,
  deliberately out of scope here).
- **Triage candidates:** none new. `tc9` (whether `check` should routinely exercise the staleness
  path) remains open per the handoff, untouched by this pass.

## Test mode
**Required:** `test-first` (TDD red -> green) for fixes 2 and 3; fix 1 is a test-quality rework of
already-shipped tests, verified by a mechanical disable-attack script rather than a fresh red/green
cycle, per the handoff's own acceptance shape.
**Satisfied:** yes.

## Evidence

### 1. Closing selector, before and after
Before (handoff's stated current shipped state): 12/12.
After:
```bash
python -m pytest tests/test_code_map.py -k "stale_tag" -q --color=no
```
**Result:** `14 passed, 101 deselected, 12 subtests passed` — exit 0. (+2 tests from fixes 2 and 3;
the rewritten 5 tests in fix 1 stayed at their original 5 method count, no new methods there.)

### 2. Disable-attack counts, before and after fix 1 — the evidence this pass exists to produce
**Before** (established by the `g6` reviewer's own reproduction, cited in `g6-review-RESULT.md`, and
matching the handoff verbatim): forcing `stale = []` after the real computation in `extract.run()` and
rerunning the selector left **9 of 12 tests green**, including all 5 named tests — every dedicated
"does not flag" test survived the whole-feature disable.

**After** — run for real, not reasoned about, via `.agent-work/issue-456/evidence/g6_disable_attack.py`:
```bash
python .agent-work/issue-456/evidence/g6_disable_attack.py
```
**Result (exit 0):**
```
{'attack_outcomes': {'test_stale_tag_first_extraction_flags_nothing': 'FAILED',
 'test_stale_tag_does_not_flag_a_reformat_across_two_extractions': 'FAILED',
 'test_stale_tag_does_not_flag_an_unrelated_anchor': 'FAILED',
 'test_stale_tag_render_report_does_not_flag_a_reformat': 'FAILED',
 'test_stale_tag_render_report_does_not_fail_the_build': 'FAILED'},
 'attack_exit': 1, 'survivors': [], 'revert_clean': True,
 'after_outcomes': {... all 5: 'PASSED'}, 'after_exit': 0,
 'after_all_named_green': True}
PASS: all 5 named tests failed under the disable attack; extract.py reverted clean; selector green again
```
All 5 named tests went RED under the attack (survivors: none). `git status --porcelain --
scripts/code_map/extract.py` confirmed clean immediately after the script's own revert (also spot-checked
independently). Selector confirmed green again afterward (12/12 in normal mode before fixes 2/3 were
added; 14/14 after the full pass).

### 3. Full suite
Baseline: **1805 passed, 2 skipped, 683 subtests, 0 failed**.
```bash
python -m pytest tests/ -q --color=no
```
**Result:** `1807 passed, 2 skipped, 684 subtests passed` in 454.07s — exit 0. Delta is +2 passed (the
two new test methods added in fixes 2 and 3) and +1 subtest (the new `subTest` loop in the
FAIL-prefix test), no regressions. Log: `.agent-work/issue-456/evidence/g6_remediate_full_suite.log`.

### 4. Fresh build then check
```bash
python -m scripts.code_map build --root .
python -m scripts.code_map check --root .
```
**Result:** build exit 0, `render_report.json` carries `"stale_tags": []` (this repo's own anchors
are unchanged since the last real build, as expected). `check` exit 0, **7/7** checks passed,
including `deterministic-rebuild`.

### 5. Clean tree, committed
```bash
git status --porcelain
```
**Result:** clean after commit `<see git log>`, explicit paths only — `scripts/code_map/extract.py`,
`scripts/code_map/render.py`, `tests/test_code_map.py`, plus this plan's own engine-provenance files
under `.agent-work/issue-456/g6-remediate/` and `.agent-work/issue-456/issue-456-g6-remediate/`, and
the two evidence artifacts under `.agent-work/issue-456/evidence/`. `git add -A` was never used; the
untracked `map/` tree and other crews' concurrent bookkeeping (`.agent-work/issue-456/context/`,
`mechanical/`, `issue-456-g5-rereview/`, `issue-456-g6-review/`, `issue-456-gb-review/`,
`execute.json.journal`) were left untouched — not mine to commit.

## TDD evidence, if required
- **Fix 2 (read-guard):** failing test observed — `json.decoder.JSONDecodeError: Unterminated string
  starting at: line 1 column 78 (char 77)`, uncaught, raised from `extract.py:1047` through
  `cli.py`, real traceback captured before the fix. Passing test observed after the fix: exit 0, one
  line containing `unreadable` in stdout, previous store treated as absent.
- **Fix 3 (FAIL->ADVISORY):** failing test observed — `AssertionError: True is not false`, subtest
  line captured verbatim: `FAIL stale tag [widget-spin]: anchor body changed, tag text did not --
  review pkg.anchors:spin and update or remove the tag`. Passing test observed after the rename.
- Refactor while green: no separate refactor pass was needed; the rename and comment tightening were
  the fix itself.

## Docs/contracts touched
- none — no docs outside the code and tests changed.

## Assumptions
- The handoff's phrase "force `stale = []` after the real computation in `extract.run()`" was read as
  inserting an override immediately after the two-line `stale = sorted(...)` assignment, at the same
  indentation level — matching the reviewer's own described attack exactly (same variable, same
  function, same code path). The disable-attack script locates the anchor programmatically (by
  searching for the assignment's own source text) rather than hardcoding a line number, so it stays
  correct if the surrounding code shifts.
- "Same fixture, same build path, same assertion mechanism" for fix 1 was read as: extend the
  existing test method with additional statements using the same helper methods (`self._extract()` /
  `self._build()`) already in use, rather than parametrizing or restructuring the test — the smallest
  change that gives each method real teeth.

## Stop conditions hit
- none.

## Out-of-scope observations
- none beyond what the handoff already named as explicitly out of scope (`tc9`, the severity ruling,
  rename sensitivity, `extract.run()` splitting, the `NamedTuple` suggestion) — all left untouched as
  directed.

## Workflow Feedback
Mandatory section. A `none` answer requires a run-specific reason: `none — confirmed after review: <what you checked>`; a bare `none` is treated as an unfilled field. This is workflow signal, not project signal: you are the only one who saw this friction — if you do not report it here, it is lost.

- **Handoff gaps:** none of substance. The handoff's acceptance shape for fix 1 (force the disable,
  rerun the selector, require all 5 red, revert, confirm clean+green) translated directly into a
  mechanical script with no ambiguity about what "done" meant.
- **Context rediscovered:** this worktree is shared with other concurrently-running crews
  (`g6-reviewer`, `gb-reviewer`, `g5-rereviewer` per `git status --porcelain`'s untracked
  `.agent-work/issue-456/issue-456-g5-rereview/`, `issue-456-g6-review/`, `issue-456-gb-review/`
  directories, and a modified `execute.json.journal` I did not touch). The handoff did not mention
  concurrent crews sharing the worktree; I had to infer it from `git status` and be careful to stage
  only my own explicit paths, never a broad `git add`, which the handoff's own constraints already
  guarded against but did not explain why the constraint exists beyond the `map/` tree.
- **Instructions improvised around:** none — the "small script file instead of long
  `--why`/heredoc" route worked cleanly for the engine calls; no long `--why` value was long enough
  to need the wrapper-script route this run's other crews found, since the engine accepted the
  `--why` strings I used directly as command-line arguments without hitting the compound-Bash
  restrictions (no `$(...)`, no heredocs, no pipes were needed in any `--why` text).
- **What would have made this easier:** the engine's own provenance directory naming
  (`.agent-work/issue-456/issue-456-g6-remediate/context/` and `.../mechanical/`, auto-created from my
  plan's `work_id`) is easy to mistake for another crew's directory at a glance, since sibling
  directories for other crews (`issue-456-g6-review/`, `issue-456-gb-review/`) follow the identical
  `issue-456-<gate>-<role>` naming pattern. A one-line note in the checklist-engine reference stating
  "this directory belongs to the work_id that created it, never assume it's a sibling crew's" would
  have saved a few minutes of git-status archaeology before I was confident about what to stage.

## Return status
`complete`
