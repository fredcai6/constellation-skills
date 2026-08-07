# tests.test_checklist_engine:Cp1252StdioTests.test_current_survives_cp1252_stdio_with_unicode_task_text
method, tests/test_checklist_engine.py:1162, 22 lines

```python
def test_current_survives_cp1252_stdio_with_unicode_task_text(self)
```

HOLE: no docstring

calls internal: Cp1252StdioTests.assertIn x2, Cp1252StdioTests.assertEqual, gate, gated
calls stdlib: builtins.str x2, builtins.dict, json.dumps, pathlib.Path, subprocess.run, tempfile.TemporaryDirectory
reads internal: SCRIPT
reads stdlib: json (module), os (module), os.environ, subprocess (module), sys (module), sys.executable, tempfile (module)
unresolved: 4 calls (dispatch-unknown-base), 3 reads (dispatch-unknown-base), 1 writes (non-name-expr)

referenced by: none found
