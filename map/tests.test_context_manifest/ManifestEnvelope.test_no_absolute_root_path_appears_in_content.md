# tests.test_context_manifest:ManifestEnvelope.test_no_absolute_root_path_appears_in_content
method, tests/test_context_manifest.py:376, 8 lines

```python
def test_no_absolute_root_path_appears_in_content(self)
```

HOLE: no docstring

calls internal: ManifestEnvelope.assertNotIn x2, ManifestEnvelope.assertIn, ManifestEnvelope.build
calls stdlib: builtins.str, pathlib.Path
reads internal: cm x3, ManifestEnvelope.roots, ManifestEnvelope.skill
unresolved: 6 calls (dispatch-unknown-base)

referenced by: none found
