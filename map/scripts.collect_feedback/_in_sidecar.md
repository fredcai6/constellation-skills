# scripts.collect_feedback:_in_sidecar
function, scripts/collect_feedback.py:269, 3 lines

```python
def _in_sidecar(entry: dict[str, str], table: dict) -> bool
```

True if any of the entry's fingerprints (new or legacy) is in `table`.

calls internal: fingerprints
calls stdlib: builtins.any

referenced by: 2 sites, this module only
