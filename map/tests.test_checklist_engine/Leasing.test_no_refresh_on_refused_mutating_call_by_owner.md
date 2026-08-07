# tests.test_checklist_engine:Leasing.test_no_refresh_on_refused_mutating_call_by_owner
method, tests/test_checklist_engine.py:744, 20 lines

```python
def test_no_refresh_on_refused_mutating_call_by_owner(self)
```

HOLE: no docstring

calls internal: Leasing.assertEqual x3, gate x2, _old_ts, gated
calls stdlib: builtins.str, pathlib.Path, tempfile.TemporaryDirectory
reads internal: E x4
reads stdlib: tempfile (module)
unresolved: 4 calls (dispatch-unknown-base), 1 writes (non-name-expr)

referenced by: none found
