# tests.test_checklist_engine:RecoveryRunnabilityAudit.test_complete_reopen_runs
method, tests/test_checklist_engine.py:2359, 10 lines

```python
def test_complete_reopen_runs(self)
```

HOLE: no docstring

calls internal: RecoveryRunnabilityAudit.assertEqual x2, _run_at x2, RecoveryRunnabilityAudit.assertIn, gate, gated
calls stdlib: pathlib.Path, tempfile.TemporaryDirectory
reads internal: E, PASS_COMMAND
reads stdlib: tempfile (module)
unresolved: 1 calls (dispatch-unknown-base)

referenced by: none found
