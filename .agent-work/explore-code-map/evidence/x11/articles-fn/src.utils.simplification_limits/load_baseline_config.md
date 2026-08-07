# src.utils.simplification_limits:load_baseline_config
function, src/utils/simplification_limits.py:182, 9 lines

```python
def load_baseline_config(path: Path = DEFAULT_BASELINE_PATH) -> tuple[frozenset[str], frozenset[str]]
```

HOLE: no docstring

calls stdlib: builtins.frozenset x4, builtins.str x2, json.loads
reads stdlib: json (module)
unresolved: 5 calls (dispatch-unknown-base)

referenced by: 3 sites, this module only
