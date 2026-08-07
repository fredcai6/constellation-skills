# tests.test_context_manifest:Serialisation.test_written_manifest_has_lf_endings_on_every_platform
method, tests/test_context_manifest.py:907, 11 lines

```python
def test_written_manifest_has_lf_endings_on_every_platform(self)
```

HOLE: no docstring

calls internal: Serialisation.assertEqual, Serialisation.assertNotIn
calls stdlib: json.loads, pathlib.Path, tempfile.TemporaryDirectory
reads internal: cm x4
reads stdlib: json (module), tempfile (module)
unresolved: 6 calls (dispatch-unknown-base)

referenced by: none found
