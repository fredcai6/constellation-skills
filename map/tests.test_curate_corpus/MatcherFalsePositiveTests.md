# tests.test_curate_corpus:MatcherFalsePositiveTests
class, tests/test_curate_corpus.py:284, 49 lines

```python
class MatcherFalsePositiveTests(TestCase)
```

Regression tests for two over-firing matcher bugs in check_description's

detectors: _exclusion_present treating 'not '/'never ' as bare
substring-anywhere (false-positives inside 'cannot'/'whenever'), and
_person_tokens colliding the 'us' pronoun with the 'US' abbreviation.

- [test_exclusion_present_no_false_positive_on_cannot](MatcherFalsePositiveTests.test_exclusion_present_no_false_positive_on_cannot.md) method: 'cannot' contains the bare substring 'not ' but carries no genuine
- [test_exclusion_present_no_false_positive_on_whenever](MatcherFalsePositiveTests.test_exclusion_present_no_false_positive_on_whenever.md) method: 'whenever' contains the bare substring 'never ' but carries no
- [test_exclusion_present_true_positive_standalone_not_never](MatcherFalsePositiveTests.test_exclusion_present_true_positive_standalone_not_never.md) method: Genuine standalone 'not'/'never' usage must still fire.
- [test_exclusion_present_true_positive_phrasal_markers](MatcherFalsePositiveTests.test_exclusion_present_true_positive_phrasal_markers.md) method: The phrasal markers are untouched by the word-boundary fix and
- [test_person_tokens_capitalized_us_abbreviation_not_flagged](MatcherFalsePositiveTests.test_person_tokens_capitalized_us_abbreviation_not_flagged.md) method: A capitalized 'US' (United States) must not be read as the 'us'
- [test_person_tokens_lowercase_us_pronoun_still_flagged](MatcherFalsePositiveTests.test_person_tokens_lowercase_us_pronoun_still_flagged.md) method: A genuine lowercase 'us' pronoun usage must still shortlist.
- [test_person_tokens_other_pronouns_unaffected_by_us_fix](MatcherFalsePositiveTests.test_person_tokens_other_pronouns_unaffected_by_us_fix.md) method: The case-sensitive carve-out is specific to 'us'; the other

referenced by: none found
