# tests.test_curate_corpus:MatcherFalsePositiveTests.test_person_tokens_capitalized_us_abbreviation_not_flagged
method, tests/test_curate_corpus.py:317, 5 lines

```python
def test_person_tokens_capitalized_us_abbreviation_not_flagged(self)
```

A capitalized 'US' (United States) must not be read as the 'us'

pronoun once lowercased for tokenizing.

calls internal: MatcherFalsePositiveTests.assertNotIn
reads internal: cc
unresolved: 1 calls (dispatch-unknown-base)

referenced by: none found
