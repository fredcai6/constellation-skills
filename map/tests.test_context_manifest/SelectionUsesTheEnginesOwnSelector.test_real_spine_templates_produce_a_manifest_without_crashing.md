# tests.test_context_manifest:SelectionUsesTheEnginesOwnSelector.test_real_spine_templates_produce_a_manifest_without_crashing
method, tests/test_context_manifest.py:513, 15 lines

```python
def test_real_spine_templates_produce_a_manifest_without_crashing(self)
```

HOLE: no docstring

calls internal: SelectionUsesTheEnginesOwnSelector.assertEqual x2, SelectionUsesTheEnginesOwnSelector.assertGreaterEqual, SelectionUsesTheEnginesOwnSelector.subTest
calls stdlib: pathlib.Path x2, builtins.len, json.loads, tempfile.TemporaryDirectory
reads internal: REAL_SPINE_TEMPLATES x2, ROOT x2, cm x2
reads stdlib: json (module), tempfile (module)
unresolved: 4 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found
