# tests.test_checklist_engine:RecoveryRunnabilityAudit.test_blocked_no_restorable_prior_only_skip_is_named_and_it_runs
method, tests/test_checklist_engine.py:2346, 12 lines

```python
def test_blocked_no_restorable_prior_only_skip_is_named_and_it_runs(self)
```

HOLE: no docstring

calls internal: RecoveryRunnabilityAudit.assertEqual x2, RecoveryRunnabilityAudit.assertNotIn x2, _run_at x2, RecoveryRunnabilityAudit.assertIn, gate, gated
calls stdlib: pathlib.Path, tempfile.TemporaryDirectory
reads internal: E, PASS_COMMAND
reads stdlib: tempfile (module)
unresolved: 1 calls (dispatch-unknown-base)

referenced by: none found
