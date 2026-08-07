# scripts.hooks.spine_rail:load_spine
function, scripts/hooks/spine_rail.py:235, 8 lines

```python
def load_spine(spine_path) -> dict | None
```

json.load the spine state file. Return None on any failure.

calls stdlib: builtins.isinstance, builtins.open, json.load
reads stdlib: builtins.Exception, builtins.dict, json (module)

referenced by: 3 sites, this module only
