# tests.test_checklist_engine:RecoveryRunnabilityAudit.test_amend_retext_check_complete_reopen_then_retry_runs
method, tests/test_checklist_engine.py:2483, 26 lines

```python
def test_amend_retext_check_complete_reopen_then_retry_runs(self)
```

HOLE: no docstring

calls internal: RecoveryRunnabilityAudit.assertEqual x3, _run_at x3, RecoveryRunnabilityAudit.assertIn, gate, gated
calls stdlib: builtins.str x2, pathlib.Path x2, json.dumps, tempfile.TemporaryDirectory
reads internal: PASS_COMMAND x3, E
reads stdlib: json (module), tempfile (module)
unresolved: 2 calls (dispatch-unknown-base)

referenced by: none found
