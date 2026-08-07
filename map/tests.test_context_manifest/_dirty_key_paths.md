# tests.test_context_manifest:_dirty_key_paths
function, tests/test_context_manifest.py:229, 15 lines

```python
def _dirty_key_paths(obj, prefix='') -> list
```

Every JSON-pointer-ish path at which a key named `dirty` occurs, at any

depth. Empty list means the field is genuinely gone rather than merely moved
somewhere the caller forgot to look (#327, #305 g4).

calls internal: _dirty_key_paths x2
calls stdlib: builtins.isinstance x2, builtins.enumerate
reads stdlib: builtins.dict, builtins.list
unresolved: 4 calls (dispatch-unknown-base)

referenced by: 3 sites, this module only
