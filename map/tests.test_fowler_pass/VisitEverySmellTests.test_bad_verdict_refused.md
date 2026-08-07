# tests.test_fowler_pass:VisitEverySmellTests.test_bad_verdict_refused
method, tests/test_fowler_pass.py:112, 3 lines

```python
def test_bad_verdict_refused(self)
```

HOLE: no docstring

calls internal: VisitEverySmellTests.assertRaises, _record, _with
reads internal: VisitEverySmellTests.rail x2
unresolved: 1 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found
