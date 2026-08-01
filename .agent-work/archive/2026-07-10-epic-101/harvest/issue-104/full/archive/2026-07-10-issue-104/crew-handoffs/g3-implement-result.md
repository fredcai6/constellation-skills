# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g3-implement` (issue #104, constellation-curator, cluster C) — golden-fixture test suite for `scripts/curate_corpus.py`.

## Completed slice
Built `tests/test_curate_corpus.py`: 18 tests across 8 classes. Each curator detector has a test proving it BITES on a planted flaw, the duplication detector is fed the AUTHENTIC pre-#108 doctrine passages (verbatim from commit 2696769), and a dedicated falsification proves flags-never-gates (curator invariant #2) — a maximally-flagged fixture still returns exit 0. No changes to `curate_corpus.py` or any skill. Drove a `gated` plan through the bundled checklist engine to green.

## Scope
**Files changed:**
- `tests/test_curate_corpus.py` (new file only)

**Also written (workflow artifact, not product):** `.agent-work/issue-104/g3-implement-plan.json` (engine state).

**Specific exclusions touched:** `no` — `curate_corpus.py`, every real skill, and every other test are untouched. `git status --short` shows only `?? tests/test_curate_corpus.py`. `git check-ignore tests/test_curate_corpus.py` exits 1 (tracked, not ignored).

## Behavior changed
`no` — test-only addition; no product runtime surface changed.

## Map Impact
- **Structural anchors touched:** `tests/test_curate_corpus.py` (new) — the detector-falsification test surface for the curator measurement tool.
- **Capabilities added/changed/affected:** detector falsification — each of curate_corpus's checks (duplication, size, invoker, description-{length,person,when-to-use,exclusion}, reference-toc, parse) now has an executable proof it fires; flags-never-gates has an executable proof it holds.
- **Constraints/assumptions touched:** honored the T6 constraint — planted duplication flaws derive verbatim from git `2696769` shapes, not invented. Newly relied on: the emphatic banner tokenizes to EXACTLY `SHINGLE_SIZE` (8) words, so it is the boundary case that still clusters (documented in the test).
- **Claims/evidence produced:** "every curator detector bites on a planted flaw" and "a maximally-flagged corpus exits 0" are now backed by passing assertions.
- **Triage candidates:** none new (see Out-of-scope observations for one latent-brittleness note).

## Test mode
**Required:** `test-after` (inspection suite over an existing G1 tool — the RED-then-GREEN loop applies to my assertions matching the tool's real strings, not to new product code).
**Satisfied:** `yes` — suite written, run, and green; assertions verified against the tool's exact status/check vocabulary read from source, not guessed.

## Evidence

### Provenance — planted duplication text is authentic pre-#108 shape (git 2696769)
```bash
$ git show 2696769:skills/implementer/SKILL.md | grep -n "misfit is compliance"
10:**Mandatory, no exceptions: once loaded, drive the checklist to completion through the engine and dispatch each step it names. Within a step, judgment is yours — when an instruction does not fit the work, do the closest compliant thing and report the misfit in your workflow feedback; reporting misfit is compliance, not deviation.**

$ git show 2696769:skills/commander/SKILL.md | grep -n "FOLLOW THIS SKILL STRICTLY"
8:**FOLLOW THIS SKILL STRICTLY. USE THE ENGINE RIGOROUSLY**

$ git show 2696769:skills/workbench/SKILL.md | grep -n "checklist_engine.py"
39:Drive a controller one step at a time with the absolute path to this installed skill's bundled `scripts/checklist_engine.py` (canonical JSON state). Do not run `scripts/checklist_engine.py` relative to the target repo unless that repo vendors the script. ...
```
All three verbatim strings are pasted into `tests/test_curate_corpus.py` as `COMPLIANCE_BOILERPLATE`, `EMPHATIC_BANNER`, and `ENGINE_INVOCATION` and used as the planted duplication signatures.

### `py -m pytest tests/test_curate_corpus.py -v` (each detector's biting test named)
```
collected 18 items

tests/test_curate_corpus.py::StatusVocabularyTests::test_status_vocabulary_is_the_expected_literals PASSED [  5%]
tests/test_curate_corpus.py::DuplicationDetectorTests::test_duplication_bites_two_authentic_signatures PASSED [ 11%]
tests/test_curate_corpus.py::DuplicationDetectorTests::test_duplication_ignores_a_single_planting PASSED [ 16%]
tests/test_curate_corpus.py::DuplicationDetectorTests::test_emphatic_banner_clusters_as_exact_shingle PASSED [ 22%]
tests/test_curate_corpus.py::SizeDetectorTests::test_oversized_body_flagged PASSED [ 27%]
tests/test_curate_corpus.py::SizeDetectorTests::test_within_budget_body_ok PASSED [ 33%]
tests/test_curate_corpus.py::InvokerDetectorTests::test_missing_invoker_flagged PASSED [ 38%]
tests/test_curate_corpus.py::InvokerDetectorTests::test_present_invoker_ok PASSED [ 44%]
tests/test_curate_corpus.py::DescriptionDetectorTests::test_confusable_skill_with_exclusion_info PASSED [ 50%]
tests/test_curate_corpus.py::DescriptionDetectorTests::test_confusable_skill_without_exclusion_flagged PASSED [ 55%]
tests/test_curate_corpus.py::DescriptionDetectorTests::test_first_person_shortlists_not_a_verdict PASSED [ 61%]
tests/test_curate_corpus.py::DescriptionDetectorTests::test_missing_when_to_use_marker_flagged PASSED [ 66%]
tests/test_curate_corpus.py::DescriptionDetectorTests::test_nonconfusable_skill_gets_no_exclusion_finding PASSED [ 72%]
tests/test_curate_corpus.py::ReferenceTocDetectorTests::test_long_reference_without_toc_flagged PASSED [ 77%]
tests/test_curate_corpus.py::ReferenceTocDetectorTests::test_short_reference_and_toc_reference_not_flagged PASSED [ 83%]
tests/test_curate_corpus.py::ParseAndCrashTests::test_main_exits_zero_even_with_unparseable_skill PASSED [ 88%]
tests/test_curate_corpus.py::ParseAndCrashTests::test_malformed_and_missing_skill_md_become_parse_rows_no_crash PASSED [ 94%]
tests/test_curate_corpus.py::FlagsNeverGatesTests::test_maximally_flagged_fixture_still_exits_zero PASSED [100%]

============================= 18 passed in 0.43s ==============================
```

Detector-to-test map (each Close-Criterion proven):
- **Duplication BITES (2 authentic signatures):** `test_duplication_bites_two_authentic_signatures` — compliance boilerplate clusters `{alpha,beta}`, engine string clusters `{delta,gamma}`; both `flagged`; asserts the shared-skills set and `finding.skill == "alpha,beta"`. Plus `test_duplication_ignores_a_single_planting` (needs >=2 skills) and `test_emphatic_banner_clusters_as_exact_shingle` (the banner = exactly 8 tokens = SHINGLE_SIZE boundary).
- **Size:** `test_oversized_body_flagged` / `test_within_budget_body_ok`.
- **Invoker (both directions):** `test_missing_invoker_flagged` / `test_present_invoker_ok`.
- **Description:** `test_first_person_shortlists_not_a_verdict` (`shortlist`, not a verdict), `test_missing_when_to_use_marker_flagged` (`flagged`), `test_confusable_skill_without_exclusion_flagged` + `test_confusable_skill_with_exclusion_info` + `test_nonconfusable_skill_gets_no_exclusion_finding` (uses real CONFUSABLE names `scout`/`cartographer`).
- **Reference-TOC:** `test_long_reference_without_toc_flagged` / `test_short_reference_and_toc_reference_not_flagged`.
- **Parse → row not crash:** `test_malformed_and_missing_skill_md_become_parse_rows_no_crash` + `test_main_exits_zero_even_with_unparseable_skill`.
- **Flags-never-gates falsification:** `test_maximally_flagged_fixture_still_exits_zero`.

### `py -m pytest tests/ -q` (full suite green)
```
........................................................................ [ 15%]
........................................................................ [ 30%]
.......................................................... [ 43%]
........................................................................ [ 58%]
........................................................................ [ 74%]
................................................................................ [ 91%]
...............s........s...............                                 [100%]
464 passed, 2 skipped, 150 subtests passed in 12.77s
```

**Result:** `pass` — 18/18 new tests green; full suite 464 passed, 2 skipped (pre-existing).

### Flags-never-gates falsification (quoted assert line)
The falsification is a real assertion, not a comment. In `test_maximally_flagged_fixture_still_exits_zero`, after asserting the fixture flags every detector, the invariant is falsified by:
```python
self.assertEqual(cc.main([str(root)]), 0)
self.assertEqual(cc.main([str(root), "--json"]), 0)
```

## TDD evidence, if required
- Test-after inspection run. The RED discipline applied to matching the tool's real vocabulary: the suite locks the exact strings via `StatusVocabularyTests` and imports the real constants (`SHINGLE_SIZE`, `SKILL_WORD_TARGET`, `REFERENCE_TOC_LINE_THRESHOLD`, `CONFUSABLE_SKILLS`) rather than hard-coding guesses, so a drift in the tool's vocabulary fails the suite.
- Passing test observed: `py -m pytest tests/test_curate_corpus.py -q` -> `18 passed`.
- Refactor while green: `no` (first-pass green).

## Docs/contracts touched
- none — test-only addition.

## Assumptions
- The engine `config_ref` `docs/agents/engine-config.json` does not exist in this worktree; the engine tolerates its absence (defaults), consistent with how the g2 plan ran. I mirrored the g2 plan's `config_ref` verbatim.
- The maximally-flagged fixture asserts the presence of each detector's flag before asserting exit 0, so a future tool change that silently stopped flagging a check would fail loudly rather than let the invariant pass vacuously.
- The banner boundary: `_words("FOLLOW THIS SKILL STRICTLY. USE THE ENGINE RIGOROUSLY")` == 8 tokens == `SHINGLE_SIZE`, so it forms exactly one shingle and clusters. The test asserts both facts, so if either `SHINGLE_SIZE` or the tokenizer changes, the test flags the interaction rather than silently mis-passing.

## Stop conditions hit
- none — every detector bit as the spec expected; no authentic shape failed to cluster; no edit to `curate_corpus.py` or a real skill was needed.

## Out-of-scope observations
- The exclusion detector is satisfied by the substring `"not "` (from `EXCLUSION_MARKERS`) appearing ANYWHERE in a confusable skill's description — e.g. a stray "cannot"/"note" wouldn't match (space-guarded) but a real word like "not" in unrelated prose would count as an exclusion clause. Not a bug for this suite (I supplied a genuine "not ..." exclusion in the confusable-with-exclusion fixture), but a curator author could get a false `info` from incidental "not". Flagging only as an observation for Commander; no action needed for G3.
- `description-person` shortlists on any of `PERSON_PRONOUNS` including `"us"` — the token `us` is common enough (I avoided it in clean fixtures) that real descriptions may shortlist on incidental matches. This is by design (SHORTLIST, human judges, T7), just noting the sensitivity.

## Workflow Feedback
- **Handoff gaps:** The handoff's Verification Commands say `py -m pytest tests/test_curate_corpus.py -v` and `py -m pytest tests/ -q`, but the engine plan template's postcondition wants a single command check. I combined both pytest calls into one `&&`-chained command check so the engine's GREEN gate exercises the full-suite regression too — worth the handoff naming the exact engine command check it expects, so implementers don't each improvise the composition.
- **Context rediscovered:** The engine CLI is `py checklist_engine.py --file FILE <verb> <id> --cond c1` and gated tasks use `advance` (not `record`/`complete`, which are survey/older verbs) — I rediscovered this from `-h` after two refusals. The handoff/skill points at `references/checklist-engine.md` but pasting the two canonical gated invocations (`attest ... --cond`, then `advance`) into the plan template comment would save the round-trip.
- **Instructions improvised around:** The plan template models a TDD red postcondition (`check: null`); for a test-after inspection run over an existing tool I collapsed to the single green postcondition per the template's own "test-after/inspection run" guidance. No real improvisation — the template covered it.
- **What would have made this easier:** One line in the handoff confirming the emphatic banner's exact-8-token behavior (it DOES cluster as a lone shingle) would have pre-answered the SHINGLE_SIZE-interaction question the handoff flagged as uncertain. I verified it empirically and encoded the assertion.

## Return status
`complete`
