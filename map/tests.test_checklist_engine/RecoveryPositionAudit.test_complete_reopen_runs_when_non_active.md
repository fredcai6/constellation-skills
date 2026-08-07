# tests.test_checklist_engine:RecoveryPositionAudit.test_complete_reopen_runs_when_non_active
method, tests/test_checklist_engine.py:2667, 10 lines

```python
def test_complete_reopen_runs_when_non_active(self)
```

HOLE: no docstring

calls internal: RecoveryPositionAudit.assertEqual x2, _run_at x2, RecoveryPositionAudit.assertIn, _make_non_active, gate, gated
calls stdlib: pathlib.Path, tempfile.TemporaryDirectory
reads internal: E, PASS_COMMAND
reads stdlib: tempfile (module)
unresolved: 1 calls (dispatch-unknown-base)

referenced by: none found
