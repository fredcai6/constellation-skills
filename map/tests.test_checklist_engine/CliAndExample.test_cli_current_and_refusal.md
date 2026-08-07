# tests.test_checklist_engine:CliAndExample.test_cli_current_and_refusal
method, tests/test_checklist_engine.py:417, 10 lines

```python
def test_cli_current_and_refusal(self)
```

HOLE: no docstring

calls internal: CliAndExample.assertEqual x2, CliAndExample.assertTrue, gate, gated
calls stdlib: builtins.str x2, pathlib.Path, tempfile.TemporaryDirectory
reads internal: E x4, FAIL_COMMAND
reads stdlib: tempfile (module)
unresolved: 4 calls (dispatch-unknown-base)

referenced by: none found
