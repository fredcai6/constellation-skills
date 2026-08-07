# tests.test_checklist_engine:Hardening.test_advance_from_child_block_refuses
method, tests/test_checklist_engine.py:456, 9 lines

```python
def test_advance_from_child_block_refuses(self)
```

HOLE: no docstring

calls internal: Hardening._review_gate, Hardening._write_child, Hardening.assertEqual, Hardening.assertRaises, Hardening.assertTrue
calls stdlib: builtins.any, builtins.str, pathlib.Path, tempfile.TemporaryDirectory
reads internal: E x2
reads stdlib: tempfile (module)
unresolved: 1 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found
