# tests.test_context_manifest:ProducerGuards.test_every_manifest_write_is_newline_pinned
method, tests/test_context_manifest.py:792, 31 lines

```python
def test_every_manifest_write_is_newline_pinned(self)
```

HOLE: no docstring

calls internal: ProducerGuards.assertEqual, ProducerGuards.assertGreaterEqual, ProducerGuards.assertIn, ProducerGuards.assertNotIn, ProducerGuards.fail
calls stdlib: ast.parse, ast.walk, builtins.isinstance, builtins.len, pathlib.Path, tempfile.TemporaryDirectory
reads internal: ProducerGuards.SOURCE, cm
reads stdlib: ast (module) x3, ast.Call, tempfile (module)
unresolved: 3 calls (dispatch-unknown-base), 2 calls (dynamic), 9 reads (dispatch-unknown-base)

referenced by: none found
