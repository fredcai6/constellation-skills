# tests.test_checklist_engine:RecoveryPositionAudit.test_unmet_postcondition_attest_runs_when_non_active
method, tests/test_checklist_engine.py:2709, 16 lines

```python
def test_unmet_postcondition_attest_runs_when_non_active(self)
```

HOLE: no docstring

calls internal: RecoveryPositionAudit.assertEqual x3, _run_at x3, RecoveryPositionAudit.assertIn, _make_non_active, gate, gated
calls stdlib: pathlib.Path, tempfile.TemporaryDirectory
reads internal: E
reads stdlib: tempfile (module)
unresolved: 1 calls (dispatch-unknown-base)

referenced by: none found
