# Review Result

## Assigned Gate
`gb` -- commit every threshold, once (issue #456)

## Result
`APPROVE`

Revised from an initial `BLOCK`. That block's one finding (below) was fixed directly by
Commander and independently re-verified here, not self-graded -- see "Recheck" section.

## Handoff compliance
All four threshold families gate-spec.json's `gb` entry names are committed in
`scripts/code_map/thresholds.py`: hole ratio (0.90 vs measured 0.673), churn ratio on
both local-edit and rename (3.0 vs measured 1.27x / 1.02x), recall floor per predicate
including `writes` (1.0 vs 4/4, 4/4, 3/3), and the template-ASCII invariant. Every one
is a ratio or run-time invariant, never an absolute count. The rename case -- signed
off "accepted-untested" at design confirm, never measured before this gate -- was
measured for the first time. Each family carries a mutation-proof falsifier test.

## Scope drift
None. `git diff bd932921..3a9b4495` touches exactly `scripts/code_map/thresholds.py`
(new) and `tests/test_code_map.py`, plus the crew's own workbench files. Every named
do-not-touch item (`is_test_module`, `SPLIT_LEGEND`, `checks.py`'s independent
declarations, the collision fixtures, `entity_symbol_join`, `page_location_matches_
content`, page headers, the 386 non-ASCII pages) is untouched. `git ls-tree -r HEAD --
map/` returns 0 -- no map page files committed. Commander's post-review fix
(`git diff 3a9b4495 -- scripts/code_map/thresholds.py`) is likewise scoped: 8 added
comment lines, zero logic change, no other file touched.

## Evidence verdict
Reproduced independently, and satisfies the "will these numbers ever tell anyone
anything" question the human's ruling poses. I built my own falsifiers rather than
reusing the implementer's, per the review handoff's explicit instruction:

- **Hole ratio (0.90 vs 0.673).** Rather than reusing the implementer's "make
  `summary_of` always return `None`" mutation, I disabled docstring emission only in
  `extract.Extractor._func` -- the code path `visit_FunctionDef` and
  `visit_AsyncFunctionDef` both alias to, covering plain functions AND methods, while
  leaving `visit_ClassDef`'s separate docstring emission intact. This is a realistic,
  single-function-path bug, not a global break. Rebuilt the real repo through the
  mutated package: holes/entities = 3537/3793 = **0.933**, crossing the ceiling. The
  ceiling fires on a plausible partial regression, not only a maximal catastrophe.
- **Churn ceilings (3.0 vs 1.27x / 1.02x).** Ran three synthetic variants on a new
  two-callee-per-caller fixture (a rename that reorders `tally()`'s comma-joined
  caller line, one that does not, and a short-to-much-longer rename): all three landed
  at the identical **1.545x**, confirming reordering and length changes never split
  one call-site mention into more than one diff line. Also ran an independent
  real-corpus rename via isolated `git worktree add` (never the implementer's test
  symbol): `scripts.checklist_engine:EngineError`, an 80-call-site **production**
  symbol, renamed to `EngineFault` restricted to the mappable corpus via
  `discovery.discover_corpus`. Result: 174 map diff lines / 348 source diff lines =
  **0.5x**. Both real-corpus renames (the implementer's 212-caller test symbol at
  1.02x, mine at an 80-caller production symbol at 0.5x) and my worst synthetic case
  (1.545x) sit well under 3.0. No realistic rename shape tested here approaches the
  ceiling.
- **Recall floors (1.0 per predicate).** Confirmed by reading `RecallFloorTests.
  setUpClass` that it builds and measures only the synthetic `_make_recall_fixture_
  repo`, never `ROOT` -- the floor cannot fire against ordinary live-corpus change.
  The `writes`-derivation-honesty claim ("no automated oracle backs any predicate") is
  independently corroborated, not just asserted: `DESIGN_SPEC.md` line 247 (critic
  TS7) records "the SCIP oracle is blind to `writes`" as the reason for the accepted
  hand-labeled-sample fix, and `extract.py`'s own module docstring has stated "stdlib
  only... No SCIP" since gate `g0` -- SCIP was never wired in for any predicate.
- **Template-ASCII invariant.** Ran two of my own mutations, distinct from the
  implementer's: (a) a non-ASCII character spliced into `TEST_NOTE` (not the
  implementer's `REFS_LEGEND` target) -- caught. (b) a non-ASCII character spliced
  into `module_index`'s own function **docstring** -- correctly NOT flagged, proving
  the docstring-exclusion branch is real and not vacuous. This closes a gap in the
  implementer's own falsifier suite: their second falsifier test proves f-string
  `{expr}` interpolation is excluded, a different and automatic AST property, but
  never exercises the docstring-exclusion branch with real non-ASCII docstring text.
  Also confirmed: `render.py` currently authors zero non-ASCII template literals,
  which combined with the 386 existing non-ASCII pages proves by construction those
  pages' non-ASCII content cannot originate from `render.py`'s own literals.
- **Suite-level evidence**, all independently reproduced both before and after
  Commander's fix: full suite `1793 passed, 2 skipped, 672 subtests passed` exit 0
  (385.97s pre-fix, 386.24s post-fix -- identical counts, confirming the fix caused no
  regression); closing selector `-k 'baseline or churn or recall or ascii'` on
  `tests/test_code_map.py`: `13 passed`, exit 0 (both runs); fresh `build` then
  `check`: `7/7`, exit 0 (both runs).

## Code/doc quality
Minimal, well-tested, and matches the file's own conventions (Fowler pass below).

## Recheck -- Commander's direct fix to the r4-quality blocker
Commander fixed the sole blocker directly (a documentation-only 8-line addition, not a
remediation crew) and asked for an independent re-verification before re-issuing the
verdict, since a Commander-authored fix must not be self-graded. Re-verified in full
(engine survey item `r7-recheck`, appended and recorded after the original
consolidation -- see `.agent-work/issue-456/gb-review/review.json`):

1. **Actionability, my own independent read, not agreement with the author.** The
   added `CHURN_RATIO_CEILING_RENAME` block names a distinct symptom -- map diff lines
   exceeding the touched call-site count -- explicitly contrasted with
   `CHURN_RATIO_CEILING_LOCAL_EDIT`'s rendering-instability symptom -- and two concrete
   things to open: the renamed symbol's own caller-list line (check it was edited in
   place, not rewrapped/re-sorted) and a possible page-path collision with an existing
   symbol. Both are grounded in the actual mechanism this review already probed
   (`render.tally()`'s single comma-joined line; the page-path collision surface).
   This is comparably concrete to the other three `WHEN THIS FIRES` lines -- it
   satisfies the constraint, not "investigate this" noise.
2. **Diff is purely additive.** `git diff 3a9b4495 -- scripts/code_map/thresholds.py`:
   8 new comment lines inserted before `CHURN_RATIO_CEILING_RENAME = 3.0`, zero logic
   change. `git status` shows no other file touched (besides Commander's own
   `execute.json` tracking). File remains pure ASCII (`str.isascii()` True) and
   `ast.parse` succeeds.
3. **No regression.** Full suite post-fix: `1793 passed, 2 skipped, 672 subtests
   passed`, exit 0, 386.24s -- identical to the pre-fix baseline. Fresh `build` then
   `check` post-fix: build exit 0 (3793 entities, matches pre-fix); `check` **7/7** all
   `ok`. Closing selector: `13 passed`, exit 0.
4. **The original scan was exhaustive, not partial.** Mechanically re-verified by
   grepping every `WHEN THIS FIRES` occurrence against every top-level constant
   definition in `thresholds.py`: 6 top-level constants total. 5 are actual thresholds
   a test checks against (`HOLE_RATIO_CEILING`, `CHURN_RATIO_CEILING_LOCAL_EDIT`,
   `CHURN_RATIO_CEILING_RENAME`, `RECALL_FLOORS`, `TEMPLATE_ASCII_INVARIANT`) -- all 5
   now carry their own `WHEN THIS FIRES` line, 1:1. The 6th, `RECALL_FLOOR_DERIVATION`,
   is not itself a checked threshold (no test asserts against it), so it is correctly
   outside this constraint's scope.

### `RECALL_FLOOR_DERIVATION`, filed precisely per Commander's request
`grep -rn RECALL_FLOOR_DERIVATION` across `scripts/`, `tests/`, and all `.py`/`.md`
files (excluding `__pycache__`): **5 total hits**. 1 is its own definition
(`thresholds.py:90`). 0 are consumers in `scripts/` or `tests/`. 1 is the code map's
own auto-generated `INDEX.md` page cataloging the symbol -- not a functional reader;
the map catalogs every symbol whether used or not. 3 are this review's own artifacts.
**Genuinely dead: zero consumers**, confirmed by grep, not asserted.

Precision on severity, since Commander asked directly whether this is the same defect
class as an unstated derivation: **it is not.** The load-bearing derivation the
handoff cared about -- why `writes` has no SCIP-independent oracle -- IS stated, and
IS what a human actually reads: it lives in `RECALL_FLOORS`'s own docstring comment
two lines above (`thresholds.py` lines 72-79), which `RECALL_FLOORS`'s own
`WHEN THIS FIRES` line points an investigator toward. `RECALL_FLOOR_DERIVATION` is a
near-verbatim, unconsumed restatement of that same docstring (both say: hand-labeled
fixture, no automated oracle, `writes` derived the same way as `calls`/`reads`, stated
rather than left implicit). The defect is **duplication with silent-drift risk** --
nothing keeps the two copies in sync, so they could diverge unnoticed -- not a missing
or dishonest derivation. Filed as triage candidate `tc1` on that basis, not softened
and not escalated past what the grep supports.

### Fowler pass (r6-fowler)
Record: `.agent-work/issue-456/gb-review/fowler-pass.json` (`verify_fowler_pass.py`
exits 0; 12 smells assessed).

- **flagged** -- speculative-generality: `thresholds.RECALL_FLOOR_DERIVATION` -- see
  above. Dead data, not misleading -- routed as triage candidate `tc1`, not a blocker.
- **overridden** -- duplicated-code: the tempfile+build setup idiom in
  `HoleRatioBaselineTests`/`RecallFloorTests`/`ChurnRatioTests` matches roughly 15
  pre-existing `TestCase` classes' own established convention in this file. Overridden
  under `global-crew.md`'s "match the surrounding code's conventions" rule -- this
  file's own repeated idiom IS the local convention here.
- All other 10 baseline smells: **absent**.

## Map impact verdict
- **Evidence supports claimed change:** yes -- see Evidence verdict above; every
  number was independently reproduced or independently re-derived by a different
  falsifier.
- **Constraints not violated:** yes -- stdlib-only, no timings in run reports, no
  `git add -A` (explicit paths only, confirmed by the diff stat), all upheld.
- **Notes match the diff:** yes -- `gb-implement-RESULT.md`'s Map Impact section
  (new module, no behavior change to rendering/checking, the resolved rename-churn
  decision) matches the diff exactly.
- **Decision candidates surfaced:** the rename-churn "accepted-untested" decision is
  resolved on the record here, matching the gate's own close criterion -- no new
  authority-requiring decision was found.
- **Durable context routed:** yes -- the dead `RECALL_FLOOR_DERIVATION` constant is
  routed as a triage candidate (`tc1`) rather than silently fixed or dropped.

## Reconciliation check
No divergence from recorded architecture. This gate closes the one open confidence
flag `DESIGN_SPEC.md` carried into `gb` (rename churn, "accepted-untested") -- now
measured and independently corroborated by this review on a different symbol.

## Blockers
None. The one blocker from the initial `BLOCK` verdict (`CHURN_RATIO_CEILING_RENAME`
missing its own `WHEN THIS FIRES` line) is fixed and independently re-verified above.

## Out-of-scope observations
- Triage candidate `tc1`: `thresholds.RECALL_FLOOR_DERIVATION` is dead -- 0 consumers,
  confirmed by grep. Duplication-with-drift-risk against `RECALL_FLOORS`'s own
  docstring, not an unstated derivation (see "Recheck" section above for the
  distinction). Delete it or wire a real consumer (e.g. have `RecallFloorTests`' own
  failure message quote it).

## Workflow Feedback

- **Handoff gaps:** none -- the handoff's five numbered attack points mapped cleanly
  onto the actual thresholds and were each independently checkable.
- **Context rediscovered:** the handoff asked me to verify the implementer's
  "measurement procedure itself was sound (isolated git worktrees)" but did not name
  which real symbol to independently re-measure with; I picked
  `scripts.checklist_engine:EngineError` (a production, ~80-call-site symbol,
  deliberately different in kind from the implementer's test-symbol measurement) by
  scanning inbound edges myself, the same technique `gb-implement-RESULT.md`
  describes using.
- **Instructions improvised around:** the checklist-engine reference doc's `reopen`
  verb doc doesn't state it is gated-only until you try it on a survey ("REFUSED:
  reopen applies to gated checklists"). When Commander asked me to re-verify a fix to
  an already-consolidated survey, I used `append` to add a new leaf item (`r7-recheck`)
  documenting the recheck, then re-`consolidate`d with `--override-reason` pointing at
  that item -- the survey-side equivalent of a gated `reopen`, keeping the record
  honest (the original `fail` stays visible for audit) rather than hand-editing state
  or silently rewriting only the result prose. Worth naming as the documented pattern
  for "re-verify after an out-of-band fix to a consolidated survey" rather than
  something each reviewer has to discover.
- **What would have made this easier:** none -- the two-instance build times (~6-7s
  per real-corpus build) made "build my own mutation, don't just trust theirs" cheap
  enough to do for every family without straining the review's time budget; worth
  naming in a future handoff so reviewers know real-corpus rebuilds are affordable
  here, not just the synthetic fixtures.

## Return status
`complete`
