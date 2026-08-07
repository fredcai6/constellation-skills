# scripts.hooks.spine_rail:_load_json_map
function, scripts/hooks/spine_rail.py:69, 8 lines

```python
def _load_json_map(path: Path) -> dict
```

Load a JSON object map; return {} on absent/corrupt/non-object.

calls stdlib: builtins.isinstance, builtins.open, json.load
reads stdlib: builtins.Exception, builtins.dict, json (module)

referenced by: 2 sites, this module only
