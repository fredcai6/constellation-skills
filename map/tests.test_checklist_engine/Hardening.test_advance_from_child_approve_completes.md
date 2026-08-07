# tests.test_checklist_engine:Hardening.test_advance_from_child_approve_completes
method, tests/test_checklist_engine.py:448, 7 lines

```python
def test_advance_from_child_approve_completes(self)
```

HOLE: no docstring

calls internal: Hardening.assertEqual x2, Hardening._review_gate, Hardening._write_child
calls stdlib: builtins.str, pathlib.Path, tempfile.TemporaryDirectory
reads internal: E
reads stdlib: tempfile (module)
unresolved: 1 calls (dispatch-unknown-base)

referenced by: none found
