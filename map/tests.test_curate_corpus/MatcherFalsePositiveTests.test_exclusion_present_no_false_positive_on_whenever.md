# tests.test_curate_corpus:MatcherFalsePositiveTests.test_exclusion_present_no_false_positive_on_whenever
method, tests/test_curate_corpus.py:297, 4 lines

```python
def test_exclusion_present_no_false_positive_on_whenever(self)
```

'whenever' contains the bare substring 'never ' but carries no

genuine exclusion clause; _exclusion_present must not fire on it.

calls internal: MatcherFalsePositiveTests.assertFalse
reads internal: cc
unresolved: 1 calls (dispatch-unknown-base)

referenced by: none found
