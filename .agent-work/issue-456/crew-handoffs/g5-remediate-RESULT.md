# Implementation Result

## Assigned gate
`g5` remediation (issue #456) — rework after `BLOCK`: the legend lies about the predicate

## Completed slice
All three pieces of work from the handoff: (1) reworded `SPLIT_LEGEND` in both hand-independent
copies to state the rule `is_test_module` actually applies, backed by a red-before-green pinning
test; (2) fixed `measure_split.py` to carry the definer dimension and report the corrected
headline; (3) verified at the boundary (full suite, fresh build/check, independence,
no-reclassification) and committed.

## Scope
**Files changed:**
- `scripts/code_map/render.py` — reworded `SPLIT_LEGEND` (line 361)
- `scripts/code_map/checks.py` — reworded `SPLIT_LEGEND` (line 301), its independent copy
- `tests/test_code_map.py` — added `test_the_legend_states_the_rule_the_predicate_actually_applies`
  to `ProductionTestCallerSplitTests`
- `.agent-work/issue-456/evidence/measure_split.py` — added the bucket x definer cross-tab
- `.agent-work/issue-456/evidence/g5_remediate_split_by_definer.json` — new evidence artifact
- `.agent-work/issue-456/evidence/g5_remediate_fullsuite.txt` — new evidence artifact
- `.agent-work/issue-456/g5-remediate-plan.json` (+ `.journal`) — this run's driven plan
- `.agent-work/issue-456-g5-remediate/context/*`, `.agent-work/issue-456-g5-remediate/mechanical/*`
  — context-governor gauge tracking for this plan (same convention as `g0-remediate`)

Committed at `588d5419`. `git add -A` never used; the untracked `map/` tree is still 0 tracked
files (`git ls-files map | wc -l` → 0). The Commander-owned `spine.json` / `crew-runs.json`
changes were left unstaged for the Commander's own commit.

**Specific exclusions touched:** no. Verified directly:
- `is_test_module`'s predicate body: **untouched** in both files (`return "tests" in parts`
  unchanged; grepped the diff — zero hits inside either function body).
- `_make_collision_repo`'s INDEX collision, `OWN_MODULE_NAMED_MUTATION` /
  `LEGEND_DROPPED_MUTATION`, `entity_symbol_join`'s two derivations, `page_location_matches_content`:
  none appear in `git diff 1f5c8a6e..588d5419 --stat` outside the five files listed above.
- Page headers: unchanged rendering path (`loc()` untouched).
- The 386 non-ASCII pages: left alone, out of scope (pre-existing docstring prose).

## Behavior changed
Yes, narrowly. The rendered `SPLIT_LEGEND` text on every entity page with a caller split now
reads "a tests package anywhere on the module path" instead of "a top-level tests package".
`is_test_module`'s actual classification behavior is **unchanged** — this is a defect in what the
page *said*, not in what the map *does*. Zero entities move between buckets as a result.

## Test mode
**Required:** test-first (TDD)
**Satisfied:** yes — red observed against the unfixed legend, green after the reword.

## Evidence

### TDD evidence: the pinning test

RED, against the unfixed legend (commit `1f5c8a6e`, before this run's edits):

```
python -m pytest tests/test_code_map.py -k test_the_legend_states_the_rule_the_predicate_actually_applies -q --color=no
```
```
F                                                                        [100%]
================================== FAILURES ===================================
_ ProductionTestCallerSplitTests.test_the_legend_states_the_rule_the_predicate_actually_applies _
...
E           AssertionError: 'top-level' unexpectedly found in "split: production vs test
caller module, by pytest's default discovery convention -- test_*.py / *_test.py naming,
or a top-level tests package. a module matching neither is counted production." : the
legend claims a TOP-LEVEL tests package while is_test_module matches a `tests` segment
anywhere on the path -- ... overclaims what the code does
1 failed, 88 deselected in 0.38s
```
Exit code: 1. Both behavioural preconditions (that a nested `pkg.sub.tests.helper` already
classifies as a test module in **both** `render.is_test_module` and `checks.is_test_module`)
passed before the failure — confirming the predicate was already correct and only the wording
was wrong.

GREEN, after rewording both `SPLIT_LEGEND` copies:

```
python -m pytest tests/test_code_map.py -k "refs or caller or legend" -q --color=no
```
```
....................                                                     [100%]
20 passed, 69 deselected in 5.86s
```
Exit code: 0. Selector went from the baseline's 19 collected to 20 (the new test), all green.

### Corrected split-by-definer headline (measure_split.py)

```
python .agent-work/issue-456/evidence/measure_split.py --out map
```
Measured twice at two points in this run (before and after the fresh rebuild in the boundary
verification below — see "Assumptions" for why the numbers moved by exactly one cell):

| bucket | prod-defined | test-defined | when measured |
|---|---|---|---|
| unused | 88 | 2340 | against the pre-existing map (matches handoff table exactly) |
| unused | 88 | 2341 | against the fresh rebuild (see below) |
| test-only | 2 | 449 | both |
| production | 873 | 0 | both |

**Corrected headline: genuinely unused production code is 88 — not the naive 2429 (2341/2429 =
96.4% of that bucket is test-defined, where zero callers is the normal expected state per
`TEST_NOTE`, not a finding).** Evidence: `.agent-work/issue-456/evidence/g5_remediate_split_by_definer.json`
(final, post-rebuild numbers).

### Full suite

```
python -m pytest tests -q --color=no
```
```
1781 passed, 2 skipped, 672 subtests passed in 356.75s (0:05:56)
```
Exit code: 0. Baseline (1780/2/672/0) + 1 — the new pinning test. Full output:
`.agent-work/issue-456/evidence/g5_remediate_fullsuite.txt`.

### Fresh build then check

```
python -m scripts.code_map build --root .
python -m scripts.code_map check --root .
```
`check`:
```
ok   no-empty-pages
ok   page-accounting
ok   refs-line-self-consistent
ok   entity-symbol-join
ok   page-location-matches-content
ok   inbound-attribution
ok   deterministic-rebuild
passed 7 checks
```
Exit code: 0. Render report: modules **111**, entities **3753**, pages **3865**.

### Independence check

```
grep -n "render import\|import render" scripts/code_map/checks.py
```
No match (exit 1) — `checks.py` imports nothing from `render.py`; the two `SPLIT_LEGEND` and
`is_test_module` copies stayed hand-independent, as required.

**Result:** pass/pass/pass/pass — all four commands above exit clean as stated.

## Docs/contracts touched
- none

## Assumptions
- **The entity/page counts moved by +1 (3752→3753 entities, 3864→3865 pages), and the split table
  moved by +1 in exactly one cell (`unused_test_defined` 2340→2341).** This is **not** a
  reclassification. This repo's `code_map` indexes its own `tests/` tree, so the new pinning test
  I wrote (`test_the_legend_states_the_rule_the_predicate_actually_applies`) is itself a newly
  mapped entity. It has no callers, so it lands in `unused` + `test-defined` — exactly the bucket
  and exactly the count (+1) a brand-new, uncalled test method should produce. The other five cells
  of the split table (88 / 2 / 449 / 873 / 0) are byte-identical to the handoff's table both before
  and after the rebuild, proving zero **existing** entities changed bucket. My own plan had
  hardcoded the pre-remediation counts into its verification check without anticipating this;
  corrected via `amend --delta ... retext-check` (authority `commander`, citing the Commander's
  own confirmation of the suite and split numbers) rather than land a check I knew would fail.
  The committed evidence json (`g5_remediate_split_by_definer.json`) holds the final, post-rebuild
  numbers (88/2341/2/449/873/0); the handoff's original table (88/2340/2/449/873/0) is reproduced
  above for direct comparison against Commander's own independent measurement.

## Stop conditions hit
- none

## Out-of-scope observations
- none new. All exclusions in the handoff's DO-NOT-TOUCH list re-verified untouched (see Scope
  above); nothing additional found.

## Workflow Feedback

- **Handoff gaps:** none — the handoff was complete and its Commander ruling held up against
  direct execution (the pinning test's behavioural half already passed before any edit, confirming
  the predicate was correct and only the wording was wrong, exactly as ruled).
- **Context rediscovered:** the fact that this repo's `code_map` self-indexes `tests/test_code_map.py`
  — so any new test added during a TDD cycle is itself a new mapped entity — is not stated anywhere
  in the handoff or `CREW_CONTEXT.md`. It cost one avoidable failed `advance` (my own plan's
  hardcoded counts) and an `amend`. Worth a line in `CREW_CONTEXT.md` for future gates that add
  tests under TDD: "adding a test to `tests/test_code_map.py` changes this repo's own map by +1
  entity/page — do not hardcode absolute counts in a verification check without accounting for it."
- **Instructions improvised around:** the context-governor HARD trip fired twice (at `m2`'s advance
  and again at `m3`'s advance) mid-run, each requiring `attach <gate> --type refresh-request --field
  seam=<gate> --field why_ref=<latest-why-id>` immediately before retrying `advance`, in the same
  breath — exactly the tc39 workaround the Commander's `STATE_NOTE.md` already documented from the
  prior attempt. Getting the latest `why_ref` required reading the plan JSON's `why_trail[-1].id`
  directly, since `current`'s `DIGEST:`/`REFRESH REQUESTED:` line does not itself surface the id to
  cite — a narrow, documented exception to "never read the JSON for state" that the doctrine itself
  seems to anticipate but does not yet close mechanically.
- **What would have made this easier:** a `current`-surfaced `latest_why_id` field (or an
  `attach ... --why-ref latest` shorthand) so the refresh-request recovery does not require reading
  the JSON file at all.

## Return status
`complete`
