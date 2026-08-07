# scripts.check_corpus_freshness:read_marker
function, scripts/check_corpus_freshness.py:105, 13 lines

```python
def read_marker(skills_root: Path) -> dict
```

HOLE: no docstring

calls internal: FreshnessError x3
calls stdlib: builtins.isinstance, json.loads
reads internal: CORPUS_MARKER x2
reads stdlib: json (module) x2, builtins.dict, json.JSONDecodeError
unresolved: 2 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
