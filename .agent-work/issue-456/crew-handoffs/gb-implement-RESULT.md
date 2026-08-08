# Implementation Result

## Assigned gate
`gb`: commit the thresholds, once

## Completed slice
Committed all four threshold families the handoff named, each as a ratio or
run-time invariant (never an absolute count), each carrying its own one-line
"what to do when this fires" in `scripts/code_map/thresholds.py`, each with a
mutation proof that it can actually fail. None were dropped; none were
widened to force a measurement to pass.

1. **Hole ratio** -- `HOLE_RATIO_CEILING = 0.90` (holes/entities). Measured
   this repo 0.673 (2525/3753) and f1Brainz (read-only) 0.572 (8603/15037),
   both far under. A canary for a catastrophic docstring-extraction
   regression, not a documentation-completeness gate.
2. **Template-ASCII by exact-line provenance** -- `TEMPLATE_ASCII_INVARIANT`.
   AST-scans `render.py`'s own literal `Constant` string nodes (minus its own
   docstrings), never the rendered pages, so it is structurally blind to the
   386 pre-existing non-ASCII pages (verbatim-reproduced source prose) --
   never a substring match against rendered text.
3. **Recall floor per predicate** -- `RECALL_FLOORS = {"calls":1.0,
   "reads":1.0, "writes":1.0}`. No SCIP is wired into this stdlib-only
   pipeline, so every predicate, `writes` included, is derived the SAME way:
   a hand-labeled 11-edge fixture, hand-traced against `extract.py`'s own
   resolution rules (R1-R8), scoring 4/4, 4/4, 3/3 on the real extractor.
4. **Churn ratio** -- `CHURN_RATIO_CEILING_LOCAL_EDIT = CHURN_RATIO_CEILING_RENAME
   = 3.0` (map diff lines / source diff lines). Measured on the real repo via
   isolated git worktrees: a local edit at **1.27x**, and -- never measured
   before this gate, signed off "accepted-untested" at design confirm -- the
   widely-referenced-symbol rename at **1.02x**. Both held. See "Findings"
   below for why the rename held.

## Scope
**Files changed:**
- `scripts/code_map/thresholds.py` (new) -- the four committed numbers, each
  with its measured derivation and its one-line action.
- `tests/test_code_map.py` -- 8 new `TestCase` classes (12 test methods) plus
  their fixture builders and helpers: `HoleRatioBaselineTests` /
  `HoleRatioBaselineFalsifierTests`, `TemplateAsciiProvenanceTests` /
  `TemplateAsciiProvenanceFalsifierTests` (+ `_template_literal_constants`),
  `RecallFloorTests` / `RecallFloorFalsifierTests` (+
  `_make_recall_fixture_repo`, `RECALL_GROUND_TRUTH`, `_recall_by_predicate`),
  `ChurnRatioTests` / `ChurnRatioFalsifierTests` (+
  `_make_churn_fixture_repo`, `_diff_line_count`, `_map_diff_lines`). Added
  `import ast` and `import difflib` to the existing import block.

**Specific exclusions touched:** no. `is_test_module`/`SPLIT_LEGEND` (both
copies), the checks.py/render.py independent-declaration design,
`_make_collision_repo`'s `INDEX` collision, `entity_symbol_join`'s two
derivations, `page_location_matches_content`, page headers (no `:<line>`),
and the 386 non-ASCII pages are all untouched -- confirmed by a fresh
`build`+`check` (below) and by `git status` showing no changes outside
`thresholds.py` (new) and `tests/test_code_map.py`.

## Behavior changed
No production rendering or checking behavior changed. `checks.CHECKS` is
still exactly 7 entries; `render.py`'s output is untouched (confirmed by
`deterministic-rebuild` staying `ok` and by the churn measurement itself,
which diffs two builds of an UNCHANGED `render.py`/`checks.py` and finds
zero difference outside the two edits it deliberately applied). This gate
adds committed **test-suite** behavior only: four new, previously-absent
threshold checks a future run's CI will go red against.

## Map Impact
- **Structural anchors touched:** new module `scripts/code_map/thresholds.py`
  (no behavior, pure constants + doc comments); `tests/test_code_map.py`
  grew by 8 classes / 12 test methods / ~6 helper functions.
- **Capabilities added/changed/affected:** the map's own test suite can now
  fail meaningfully on four regression classes it previously could not name:
  a docstring-extraction collapse, a censored/mis-authored template literal,
  an extraction recall regression on any predicate (including `writes`), and
  disproportionate map churn from a small edit.
- **Constraints/assumptions touched:** the recall floors' derivation (a
  small, hand-labeled, non-statistical fixture) and the ASCII invariant's
  scope (render.py's own literals only, never rendered pages) are both new,
  stated assumptions -- see `thresholds.py`'s own docstrings, which are the
  durable home for both.
- **Decision candidates / resolved decisions:** the widely-referenced-rename
  churn question that DESIGN_SPEC left "accepted-untested" is now resolved:
  measured at 1.02x, held. Recorded here and in `thresholds.py`, not as a
  new decision file -- this gate's whole job was to make that measurement.
- **Claims/evidence produced:** all four families' real-corpus measurements
  are in "Evidence" below, reproducible from the commands given.
- **Trust limitations / drift found:** the recall floor's 11-edge fixture is
  explicitly NOT a claim of statistical coverage over the extractor's whole
  error surface -- stated in `RECALL_GROUND_TRUTH`'s own docstring. The
  churn ceiling's real-corpus numbers are pinned to commit `bd932921`; a
  future measurement on a materially different corpus shape should re-run
  the same worktree procedure rather than assume these numbers still hold.
- **Triage candidates:** none surfaced beyond the workflow feedback below.

## Test mode
**Required:** evidence-only / test-after (threshold commitment, not a defect
fix -- no pre-existing broken behavior to TDD red-green against).
**Satisfied:** yes, with a mutation proof standing in for the red step on
every family (see "TDD evidence" below) -- each proves the new check goes
red on a real fixture/mutation before the real corpus's own green is
reported as evidence.

## Evidence

```bash
python -m pytest tests/test_code_map.py -k "baseline or churn or recall or ascii" -q --color=no
```
**Result:** 13 passed, 88 deselected. (Pre-gb baseline, verified directly
against the untouched worktree at commit `bd932921` -- see "Workflow
Feedback": **1** test collected, not the 17 the handoff stated. +12 is
exactly this gate's four families at 3 tests each.)

```bash
python -m scripts.code_map build
python -m scripts.code_map check
```
**Result:** build and check both exit 0. `check`: **7/7** (`no-empty-pages`,
`page-accounting`, `refs-line-self-consistent`, `entity-symbol-join`,
`page-location-matches-content`, `inbound-attribution`,
`deterministic-rebuild`, all `ok`). Report: modules=111, entities=3793,
pages=3905 (grown from the entering baseline 111/3753/3865 because this
repo self-indexes `tests/`, and this gate's own tests are part of the
mapped corpus -- `tc47`'s prediction, confirmed again).

**Family 1, hole ratio -- this repo and f1Brainz:**
```bash
python -c "import json; d=json.load(open('.code-map/render_report.json')); print(d['holes']/d['entities'])"
```
This repo: 2525/3753 = **0.673**. f1Brainz (read-only, built to scratch,
never touching its working tree): 8603/15037 = **0.572**. Both under the
0.90 ceiling with wide margin, on two corpora of very different shape and
scale.

**Family 4, churn ratio -- this repo, isolated git worktrees (commit
`bd932921`):**
- Local edit (`scripts/code_map/discovery.is_mappable`'s docstring):
  14 map diff lines / 11 source diff lines = **1.27x**.
- Rename (`tests.test_checklist_engine:gated` -> `gated_plan`, the real
  corpus's highest-fan-in internal symbol -- 212 distinct caller entities,
  identified by an inbound scan of a fresh build's `statements.jsonl`, not
  guessed -- across the one file that holds all 212 callers): 466 map diff
  lines / 458 source diff lines = **1.02x**, touching 217 of 3865 pages.

Both worktrees were created with `git worktree add`, measured, and removed
with `git worktree remove --force`; the main worktree was never touched by
either edit.

## TDD evidence (mutation proofs, per family)

- **Family 1:** `HoleRatioBaselineFalsifierTests` -- `render.summary_of`
  mutated to always return `None` (a copy, via `mutated_package`): ratio
  goes from 0.0 (intact fixture, positive control) to 1.0, crossing 0.90.
- **Family 2:** `TemplateAsciiProvenanceFalsifierTests` -- an em-dash spliced
  into `REFS_LEGEND`'s own literal text is caught; a non-ASCII value
  threaded through an f-string `{expr}` (standing in for a docstring
  summary) is correctly NOT flagged.
- **Family 3:** `RecallFloorFalsifierTests` -- `extract._store`'s
  `self._ref(t, "writes")` anchor (the Name/Attribute write branch)
  retargeted to `"reads"`: writes recall drops to 1/3 = 0.333, under the 1.0
  floor; calls/reads recall stay at 1.0, proving the mutation is scoped to
  the predicate it claims to break.
- **Family 4:** `ChurnRatioFalsifierTests` -- `render.module_index`'s
  per-module `holes = sum(1 for k in members if not summary_of(k))` mutated
  to sum over `entities` (the whole corpus) instead of `members` (this
  module only): deleting ONE docstring anywhere then ripples the corpus-wide
  count into every module's `INDEX.md`, crossing the 3x ceiling on a fixture
  where the honest local edit (family 4's own positive control) stays under
  it.
- Refactor while green: yes -- `thresholds.py`'s docstrings were rewritten
  once real numbers replaced the pre-measurement placeholders; no test
  changed as a result.

## Findings

**The widely-referenced-symbol rename churn ceiling HELD, on the first-ever
measurement.** 1.02x, essentially flat, not a near-miss. The reason is
structural, not luck, and worth carrying forward: a pure identifier rename
changes exactly one line per call site on BOTH sides of the ratio -- the
source line naming it, and the caller's own rendered "uses" line naming it
back. That 1:1 relationship holds regardless of HOW MANY callers exist, so
the diff-**lines** ratio stays near 1x even though the diff-**pages** count
(217 of 3865, a number nobody committed a ceiling against) looks alarming
in isolation. This is a real vindication of the design process's choice to
measure churn in diff LINES rather than diff PAGES (DESIGN_SPEC line 180) --
had this gate measured pages instead, "the rename blew through the ceiling"
would have been the honest finding, and it would have been the wrong
finding, an artifact of the wrong unit rather than an actual regression.

No family required dropping or widening. All four held.

## Docs/contracts touched
- none outside `scripts/code_map/thresholds.py` and `tests/test_code_map.py`
  themselves -- no README, GLOSSARY, or architecture doc references these
  thresholds yet.

## Assumptions
- The hole-ratio ceiling (0.90) and both churn ceilings (3.0) are commitments
  against THIS repo's and f1Brainz's measured shape; a corpus of a very
  different character (e.g., near-100% undocumented, or a pathologically
  interconnected module graph) was not measured and is not claimed to be
  covered.
- The recall floor's fixture is a deliberately small, hand-verified sample
  (11 edges across 3 predicates) -- stated as such in `RECALL_GROUND_TRUTH`'s
  own docstring, not claimed as a statistical measure of extractor recall
  across the whole corpus.

## Stop conditions hit
- Four HARD context-governor trips (15% -> 21% -> 24% -> 28% fill), one per
  gate item (m0 through m4's boundaries). Each was handled per doctrine:
  attach a `refresh-request` citing the CURRENT latest `why_trail[-1].id`,
  then use the one unblocked `advance` to write a comprehensive digest
  capturing full design/measurement state, so a relaunched agent could
  cold-start from `current` alone with nothing lost. After the first (at m0,
  before any code existed), reported status to `team-lead` via `SendMessage`
  and continued in the same session rather than fully idling, since every
  subsequent trip landed at a clean, fully-documented seam and ending the
  session would have left the `IMPLEMENTER_RESULT` file absent against this
  gate's own explicit instruction not to do that.

## Out-of-scope observations
- none found beyond what is already named in "Workflow Feedback" below.

## Workflow Feedback

- **Handoff gaps:** the handoff states the closing selector "collects 17
  tests today." Directly verified against the untouched pre-gb worktree
  (commit `bd932921`, via an isolated `git worktree add`, never the main
  worktree): it collects **1**, not 17
  (`DeterminismTests.test_determinism_baseline_an_unmutated_package_copy_passes`).
  This did not block the gate -- the selector still demonstrably collects a
  correctly-named, non-zero, passing set after this gate's work (13, all
  four families represented, +12 exactly matching the new tests) -- but the
  17 claim itself was wrong and worth correcting for whatever record cited
  it (`STATE_NOTE.md`'s scanner table). Given `tc47`/`tc38` exist specifically
  because a stale selector count went unchecked before, I verified this one
  by hand rather than trusting the printed number, per this gate's own
  standing instruction to overrule the handoff when it can be falsified.
- **Context rediscovered:** none beyond what "Instructions improvised
  around" below covers -- the handoff's four-family breakdown, the
  no-absolute-counts proof, and the do-not-touch list all matched the actual
  source closely enough that nothing needed rediscovering.
- **Instructions improvised around:** the handoff's illustrative ratio
  example for churn ("`churn_pages / changed_entities`") does not match the
  unit the design process actually measured and signed off on at cycle-4
  ("map diff lines vs source diff lines", DESIGN_SPEC line 180). I used the
  DESIGN_SPEC's own unit (diff lines) rather than the handoff's illustrative
  one, since the handoff's ratio was offered as an example of the SHAPE
  ("a ratio, not a count"), not as the specific committed unit, and diverging
  from established prior art without a stated reason would have been the
  actual deviation. Recording this so a reader comparing the handoff's
  wording to `thresholds.py` does not read it as a mismatch I missed.
  Separately, no automated oracle (SCIP or otherwise) is wired into this
  stdlib-only pipeline, so "recall floor per predicate" was satisfied with a
  hand-labeled fixture rather than the SCIP-based approach the handoff's
  own prose gestures toward for `calls`/`reads` -- stated explicitly in
  `RECALL_GROUND_TRUTH`'s docstring so this is a visible choice, not a
  silent substitution.
- **What would have made this easier:** a single "verify every selector
  count in this handoff by hand before trusting it, the same way you verify
  every other claim" line, next to the `tc38`/`tc47` warning -- the warning
  as written reads as "make sure YOUR new tests match the selector," which
  I did, but it does not as directly prompt re-verifying a PRE-EXISTING
  count the handoff itself asserts.

## Return status
`complete`
