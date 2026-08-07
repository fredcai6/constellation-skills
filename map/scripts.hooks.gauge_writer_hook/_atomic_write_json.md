# scripts.hooks.gauge_writer_hook:_atomic_write_json
function, scripts/hooks/gauge_writer_hook.py:402, 6 lines

```python
def _atomic_write_json(path: Path, record: dict) -> None
```

HOLE: no docstring

calls stdlib: builtins.open, json.dump, os.replace
reads stdlib: json (module), os (module)
unresolved: 2 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: 3 sites, this module only
