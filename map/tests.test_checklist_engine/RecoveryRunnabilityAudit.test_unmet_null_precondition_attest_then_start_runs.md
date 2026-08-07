# tests.test_checklist_engine:RecoveryRunnabilityAudit.test_unmet_null_precondition_attest_then_start_runs
method, tests/test_checklist_engine.py:2377, 14 lines

```python
def test_unmet_null_precondition_attest_then_start_runs(self)
```

HOLE: no docstring

calls internal: RecoveryRunnabilityAudit.assertEqual x3, _run_at x3, RecoveryRunnabilityAudit.assertIn, gate, gated
calls stdlib: pathlib.Path, tempfile.TemporaryDirectory
reads internal: E
reads stdlib: tempfile (module)
unresolved: 1 calls (dispatch-unknown-base)

referenced by: none found
