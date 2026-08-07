# tests.test_fowler_pass:VisitEverySmellTests.test_missing_smell_refused
method, tests/test_fowler_pass.py:95, 6 lines

```python
def test_missing_smell_refused(self)
```

HOLE: no docstring

calls internal: VisitEverySmellTests.assertRaises, _all_absent, _record
reads internal: VisitEverySmellTests.rail x2
unresolved: 1 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found
