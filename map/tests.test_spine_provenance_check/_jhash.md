# tests.test_spine_provenance_check:_jhash
function, tests/test_spine_provenance_check.py:264, 7 lines

```python
def _jhash(entry: dict) -> str
```

Re-derive an entry hash exactly as the engine + check do.

calls stdlib: hashlib.sha256, json.dumps
reads stdlib: hashlib (module), json (module)
unresolved: 3 calls (dispatch-unknown-base)

referenced by: 3 sites, this module only
