# tests.test_context_manifest:ManifestEnvelope.test_a_varying_field_placed_outside_run_cannot_become_content
method, tests/test_context_manifest.py:400, 23 lines

```python
def test_a_varying_field_placed_outside_run_cannot_become_content(self)
```

HOLE: no docstring

- [leaky_content](ManifestEnvelope.test_a_varying_field_placed_outside_run_cannot_become_content.leaky_content.md) method: HOLE: no docstring

calls internal: ManifestEnvelope.assertEqual x2, ManifestEnvelope.assertRaises x2, ManifestEnvelope.assertNotIn, ManifestEnvelope.build
calls stdlib: builtins.set x4, builtins.dict, pathlib.Path.cwd
reads internal: cm x2
reads stdlib: builtins.AssertionError x2, pathlib.Path
unresolved: 3 calls (dispatch-unknown-base)

referenced by: none found
