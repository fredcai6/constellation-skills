# tests.test_curate_corpus:MatcherFalsePositiveTests.test_exclusion_present_no_false_positive_on_cannot
method, tests/test_curate_corpus.py:292, 4 lines

```python
def test_exclusion_present_no_false_positive_on_cannot(self)
```

'cannot' contains the bare substring 'not ' but carries no genuine

exclusion clause; _exclusion_present must not fire on it.

calls internal: MatcherFalsePositiveTests.assertFalse
reads internal: cc
unresolved: 1 calls (dispatch-unknown-base)

referenced by: none found
