# tests.test_checklist_engine:Waiver.test_cli_waive_refused_without_policy
method, tests/test_checklist_engine.py:620, 8 lines

```python
def test_cli_waive_refused_without_policy(self)
```

HOLE: no docstring

calls internal: Waiver.assertEqual, gate, gated
calls stdlib: builtins.str, pathlib.Path, tempfile.TemporaryDirectory
reads internal: E x2, FAIL_COMMAND
reads stdlib: tempfile (module)
unresolved: 2 calls (dispatch-unknown-base)

referenced by: none found
