# tests.test_checklist_engine:Hardening.test_config_ref_resolves_rework_cap
method, tests/test_checklist_engine.py:473, 16 lines

```python
def test_config_ref_resolves_rework_cap(self)
```

HOLE: no docstring

calls internal: Hardening.assertEqual, Hardening.assertIn, gate
calls stdlib: pathlib.Path x4, tempfile.TemporaryDirectory, types.SimpleNamespace
reads internal: E x5, PASS_COMMAND
reads stdlib: tempfile (module), types (module)
unresolved: 5 calls (dispatch-unknown-base), 1 writes (non-name-expr)

referenced by: none found
