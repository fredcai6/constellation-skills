# tests.test_checklist_engine:Inv3StartNonActiveEnumeration.test_reopen_cascade_reproduces_the_ordinary_reachability_path
method, tests/test_checklist_engine.py:2813, 22 lines

```python
def test_reopen_cascade_reproduces_the_ordinary_reachability_path(self)
```

HOLE: no docstring

calls internal: Inv3StartNonActiveEnumeration.assertEqual x5, Inv3StartNonActiveEnumeration.assertIn x3, _run_at x2, gate x2, Inv3StartNonActiveEnumeration.assertNotIn, gated
calls stdlib: pathlib.Path, tempfile.TemporaryDirectory
reads internal: E x3, PASS_COMMAND x2
reads stdlib: tempfile (module)
unresolved: 3 calls (dispatch-unknown-base)

referenced by: none found
