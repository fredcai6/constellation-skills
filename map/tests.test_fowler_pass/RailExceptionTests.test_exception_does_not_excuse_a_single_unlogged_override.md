# tests.test_fowler_pass:RailExceptionTests.test_exception_does_not_excuse_a_single_unlogged_override
method, tests/test_fowler_pass.py:204, 8 lines

```python
def test_exception_does_not_excuse_a_single_unlogged_override(self)
```

HOLE: no docstring

calls internal: RailExceptionTests.assertRaises, _record, _with
reads internal: RailExceptionTests.rail x2
unresolved: 1 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found
