# tests.test_checklist_engine:GitChangePolicyCollectorIntegration.test_evaluator_over_collected_files_flags_deny_glob
method, tests/test_checklist_engine.py:1143, 12 lines

```python
def test_evaluator_over_collected_files_flags_deny_glob(self)
```

HOLE: no docstring

calls internal: GitChangePolicyCollectorIntegration._git x4, GitChangePolicyCollectorIntegration.assertTrue, _policy
calls stdlib: builtins.any, pathlib.Path, tempfile.TemporaryDirectory
reads internal: E x2
reads stdlib: tempfile (module)
unresolved: 4 calls (dispatch-unknown-base)

referenced by: none found
