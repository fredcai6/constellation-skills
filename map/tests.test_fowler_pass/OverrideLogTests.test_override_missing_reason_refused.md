# tests.test_fowler_pass:OverrideLogTests.test_override_missing_reason_refused
method, tests/test_fowler_pass.py:176, 5 lines

```python
def test_override_missing_reason_refused(self)
```

HOLE: no docstring

calls internal: OverrideLogTests.assertRaises, _record, _with
reads internal: OverrideLogTests.rail x2
unresolved: 1 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found
