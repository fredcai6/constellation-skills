# tests.test_checklist_engine:RecoveryRunnabilityAudit.test_unmet_command_precondition_fix_and_retry_runs
method, tests/test_checklist_engine.py:2416, 19 lines

```python
def test_unmet_command_precondition_fix_and_retry_runs(self)
```

HOLE: no docstring

calls internal: RecoveryRunnabilityAudit.assertEqual x2, _run_at x2, RecoveryRunnabilityAudit.assertIn, gate, gated
calls stdlib: pathlib.Path, tempfile.TemporaryDirectory
reads internal: E x3, FAIL_COMMAND, PASS_COMMAND
reads stdlib: tempfile (module)
unresolved: 3 calls (dispatch-unknown-base), 1 writes (non-name-expr)

referenced by: none found
