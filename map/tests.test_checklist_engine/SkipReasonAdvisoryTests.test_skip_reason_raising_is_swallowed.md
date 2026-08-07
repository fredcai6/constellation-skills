# tests.test_checklist_engine:SkipReasonAdvisoryTests.test_skip_reason_raising_is_swallowed
method, tests/test_checklist_engine.py:3477, 5 lines

```python
def test_skip_reason_raising_is_swallowed(self)
```

HOLE: no docstring

calls internal: SkipReasonAdvisoryTests.assertEqual
calls stdlib: builtins.RuntimeError, pathlib.Path, tempfile.TemporaryDirectory
reads internal: E x2
reads stdlib: tempfile (module), unittest.mock, unittest.mock.patch
unresolved: 1 calls (chained-attribute), 1 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found
