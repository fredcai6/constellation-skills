# tests.test_explorer_templates:ExplorerSpineCrossCheck.test_instantiates_and_engine_can_claim_and_start
method, tests/test_explorer_templates.py:315, 34 lines

```python
def test_instantiates_and_engine_can_claim_and_start(self)
```

HOLE: no docstring

calls internal: ExplorerSpineCrossCheck.assertIn x3, ExplorerSpineCrossCheck.assertEqual x2, ExplorerSpineCrossCheck.assertTrue x2, ExplorerSpineCrossCheck.assertIsNotNone, ExplorerSpineCrossCheck.assertNotIn
calls stdlib: builtins.str x4, subprocess.run x2, pathlib.Path, tempfile.TemporaryDirectory
reads internal: ROOT x3, ENGINE x2, ExplorerSpineCrossCheck.iwa, SPINE_TEMPLATE
reads stdlib: subprocess (module) x2, sys (module) x2, sys.executable x2, tempfile (module)
unresolved: 5 calls (dispatch-unknown-base), 5 reads (dispatch-unknown-base)

referenced by: none found
