# tests.test_checklist_engine:GitChangePolicyCollectorIntegration.test_staged_collector_reports_path_size_binary
method, tests/test_checklist_engine.py:1126, 16 lines

```python
def test_staged_collector_reports_path_size_binary(self)
```

HOLE: no docstring

calls internal: GitChangePolicyCollectorIntegration._git x4, GitChangePolicyCollectorIntegration.assertIn x2, GitChangePolicyCollectorIntegration.assertEqual, GitChangePolicyCollectorIntegration.assertFalse, GitChangePolicyCollectorIntegration.assertTrue
calls stdlib: pathlib.Path, tempfile.TemporaryDirectory
reads internal: E
reads stdlib: tempfile (module)
unresolved: 3 calls (dispatch-unknown-base)

referenced by: none found
