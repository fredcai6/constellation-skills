# tests.test_checklist_engine:RecoveryRunnabilityAudit.test_amend_retext_check_skipped_names_no_runnable_command
method, tests/test_checklist_engine.py:2534, 18 lines

```python
def test_amend_retext_check_skipped_names_no_runnable_command(self)
```

HOLE: no docstring

calls internal: RecoveryRunnabilityAudit.assertEqual, RecoveryRunnabilityAudit.assertNotIn, _run_at, gate, gated
calls stdlib: pathlib.Path x2, builtins.str, json.dumps, tempfile.TemporaryDirectory
reads internal: PASS_COMMAND x2, E
reads stdlib: json (module), tempfile (module)
unresolved: 2 calls (dispatch-unknown-base)

referenced by: none found
