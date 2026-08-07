# tests.test_checklist_engine:RecoveryPositionAudit.test_amend_drop_blocked_pending_prior_resume_runs_when_non_active
method, tests/test_checklist_engine.py:2739, 18 lines

```python
def test_amend_drop_blocked_pending_prior_resume_runs_when_non_active(self)
```

HOLE: no docstring

calls internal: RecoveryPositionAudit.assertEqual x3, _run_at x3, RecoveryPositionAudit.assertIn, _make_non_active, gate, gated
calls stdlib: builtins.str x2, pathlib.Path x2, json.dumps, tempfile.TemporaryDirectory
reads internal: E, PASS_COMMAND
reads stdlib: json (module), tempfile (module)
unresolved: 2 calls (dispatch-unknown-base)

referenced by: none found
