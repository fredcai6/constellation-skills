# tests.test_checklist_engine:RecoveryPositionAudit.test_unmet_precondition_recovery_is_unreachable_while_non_active
method, tests/test_checklist_engine.py:2678, 30 lines

```python
def test_unmet_precondition_recovery_is_unreachable_while_non_active(self)
```

HOLE: no docstring

calls internal: RecoveryPositionAudit.assertEqual x5, _run_at x5, RecoveryPositionAudit.assertIn x3, RecoveryPositionAudit.assertNotIn, _make_non_active, gate, gated
calls stdlib: pathlib.Path, tempfile.TemporaryDirectory
reads internal: E
reads stdlib: tempfile (module)
unresolved: 1 calls (dispatch-unknown-base)

referenced by: none found
