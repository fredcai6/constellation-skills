# tests.test_curate_corpus
tests/test_curate_corpus.py, 402 lines, 23 holes

Golden-fixture suite for scripts/curate_corpus.py.

Each test builds a throwaway skills/ corpus in a tempfile.TemporaryDirectory,
runs the curator's mechanical checks over it, and asserts that a specific
detector BITES (a detector that finds nothing on a planted flaw is a broken
detector). The planted DUPLICATION flaws are the AUTHENTIC pre-#108 doctrine
passages (sourced verbatim from commit 2696769, before cluster A single-sourced
them) so the golden test measures the real drift the epic eliminated.

The final test FALSIFIES curator invariant #2 (flags-never-gates): a corpus with
every detector firing at once must still exit 0.

Stdlib + unittest only; asserts against the EXACT status/check strings read from
curate_corpus.py.

imports stdlib: importlib.util, pathlib.Path, sys, tempfile, unittest
imported by: none found

```python
ROOT = Path(__file__).resolve().parents[1]
CURATE = ROOT / 'scripts' / 'curate_corpus.py'
cc = load_module('curate_corpus', CURATE)
COMPLIANCE_BOILERPLATE = 'Mandatory, no exceptions: once loaded, drive the checklist to completion through the e...
EMPHATIC_BANNER = 'FOLLOW THIS SKILL STRICTLY. USE THE ENGINE RIGOROUSLY'
ENGINE_INVOCATION = "Drive a controller one step at a time with the absolute path to this installed skill's...
```

- [load_module](load_module.md) function: HOLE: no docstring
- [write_skill](write_skill.md) function: Write skills/<name>/SKILL.md (+ optional references/*.md) under root.
- [write_raw_skill](write_raw_skill.md) function: Write a SKILL.md with fully raw (possibly malformed) content.
- [clean_frontmatter](clean_frontmatter.md) function: A third-person, budget-clean, non-confusable frontmatter baseline so that
- [find](find.md) function: HOLE: no docstring
- [StatusVocabularyTests](StatusVocabularyTests.md) class: Lock the exact status strings the whole suite asserts against.
  - [StatusVocabularyTests.test_status_vocabulary_is_the_expected_literals](StatusVocabularyTests.test_status_vocabulary_is_the_expected_literals.md) method: HOLE: no docstring
- [DuplicationDetectorTests](DuplicationDetectorTests.md) class: HOLE: no docstring
  - [DuplicationDetectorTests.test_duplication_bites_two_authentic_signatures](DuplicationDetectorTests.test_duplication_bites_two_authentic_signatures.md) method: Compliance boilerplate in {alpha,beta} and the engine-invocation
  - [DuplicationDetectorTests.test_duplication_ignores_a_single_planting](DuplicationDetectorTests.test_duplication_ignores_a_single_planting.md) method: A signature in only one skill must NOT cluster (needs >= 2 skills).
  - [DuplicationDetectorTests.test_emphatic_banner_clusters_as_exact_shingle](DuplicationDetectorTests.test_emphatic_banner_clusters_as_exact_shingle.md) method: The banner tokenizes to exactly SHINGLE_SIZE (8) words
- [SizeDetectorTests](SizeDetectorTests.md) class: HOLE: no docstring
  - [SizeDetectorTests.test_oversized_body_flagged](SizeDetectorTests.test_oversized_body_flagged.md) method: HOLE: no docstring
  - [SizeDetectorTests.test_within_budget_body_ok](SizeDetectorTests.test_within_budget_body_ok.md) method: HOLE: no docstring
- [InvokerDetectorTests](InvokerDetectorTests.md) class: HOLE: no docstring
  - [InvokerDetectorTests.test_missing_invoker_flagged](InvokerDetectorTests.test_missing_invoker_flagged.md) method: HOLE: no docstring
  - [InvokerDetectorTests.test_present_invoker_ok](InvokerDetectorTests.test_present_invoker_ok.md) method: HOLE: no docstring
- [DescriptionDetectorTests](DescriptionDetectorTests.md) class: HOLE: no docstring
  - [DescriptionDetectorTests.test_first_person_shortlists_not_a_verdict](DescriptionDetectorTests.test_first_person_shortlists_not_a_verdict.md) method: HOLE: no docstring
  - [DescriptionDetectorTests.test_missing_when_to_use_marker_flagged](DescriptionDetectorTests.test_missing_when_to_use_marker_flagged.md) method: HOLE: no docstring
  - [DescriptionDetectorTests.test_confusable_skill_without_exclusion_flagged](DescriptionDetectorTests.test_confusable_skill_without_exclusion_flagged.md) method: A skill named in curate_corpus's CONFUSABLE set whose description has
  - [DescriptionDetectorTests.test_confusable_skill_with_exclusion_info](DescriptionDetectorTests.test_confusable_skill_with_exclusion_info.md) method: HOLE: no docstring
  - [DescriptionDetectorTests.test_nonconfusable_skill_gets_no_exclusion_finding](DescriptionDetectorTests.test_nonconfusable_skill_gets_no_exclusion_finding.md) method: HOLE: no docstring
- [ReferenceTocDetectorTests](ReferenceTocDetectorTests.md) class: HOLE: no docstring
  - [ReferenceTocDetectorTests.test_long_reference_without_toc_flagged](ReferenceTocDetectorTests.test_long_reference_without_toc_flagged.md) method: HOLE: no docstring
  - [ReferenceTocDetectorTests.test_short_reference_and_toc_reference_not_flagged](ReferenceTocDetectorTests.test_short_reference_and_toc_reference_not_flagged.md) method: HOLE: no docstring
- [MatcherFalsePositiveTests](MatcherFalsePositiveTests.md) class: Regression tests for two over-firing matcher bugs in check_description's
  - [MatcherFalsePositiveTests.test_exclusion_present_no_false_positive_on_cannot](MatcherFalsePositiveTests.test_exclusion_present_no_false_positive_on_cannot.md) method: 'cannot' contains the bare substring 'not ' but carries no genuine
  - [MatcherFalsePositiveTests.test_exclusion_present_no_false_positive_on_whenever](MatcherFalsePositiveTests.test_exclusion_present_no_false_positive_on_whenever.md) method: 'whenever' contains the bare substring 'never ' but carries no
  - [MatcherFalsePositiveTests.test_exclusion_present_true_positive_standalone_not_never](MatcherFalsePositiveTests.test_exclusion_present_true_positive_standalone_not_never.md) method: Genuine standalone 'not'/'never' usage must still fire.
  - [MatcherFalsePositiveTests.test_exclusion_present_true_positive_phrasal_markers](MatcherFalsePositiveTests.test_exclusion_present_true_positive_phrasal_markers.md) method: The phrasal markers are untouched by the word-boundary fix and
  - [MatcherFalsePositiveTests.test_person_tokens_capitalized_us_abbreviation_not_flagged](MatcherFalsePositiveTests.test_person_tokens_capitalized_us_abbreviation_not_flagged.md) method: A capitalized 'US' (United States) must not be read as the 'us'
  - [MatcherFalsePositiveTests.test_person_tokens_lowercase_us_pronoun_still_flagged](MatcherFalsePositiveTests.test_person_tokens_lowercase_us_pronoun_still_flagged.md) method: A genuine lowercase 'us' pronoun usage must still shortlist.
  - [MatcherFalsePositiveTests.test_person_tokens_other_pronouns_unaffected_by_us_fix](MatcherFalsePositiveTests.test_person_tokens_other_pronouns_unaffected_by_us_fix.md) method: The case-sensitive carve-out is specific to 'us'; the other
- [ParseAndCrashTests](ParseAndCrashTests.md) class: HOLE: no docstring
  - [ParseAndCrashTests.test_malformed_and_missing_skill_md_become_parse_rows_no_crash](ParseAndCrashTests.test_malformed_and_missing_skill_md_become_parse_rows_no_crash.md) method: HOLE: no docstring
  - [ParseAndCrashTests.test_main_exits_zero_even_with_unparseable_skill](ParseAndCrashTests.test_main_exits_zero_even_with_unparseable_skill.md) method: HOLE: no docstring
- [FlagsNeverGatesTests](FlagsNeverGatesTests.md) class: HOLE: no docstring
  - [FlagsNeverGatesTests._build_maximally_flagged_corpus](FlagsNeverGatesTests._build_maximally_flagged_corpus.md) method: Every detector firing at once in one corpus.
  - [FlagsNeverGatesTests.test_maximally_flagged_fixture_still_exits_zero](FlagsNeverGatesTests.test_maximally_flagged_fixture_still_exits_zero.md) method: HOLE: no docstring
