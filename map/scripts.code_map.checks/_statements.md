# scripts.code_map.checks:_statements
function, scripts/code_map/checks.py:32, 4 lines

```python
def _statements(artifacts)
```

HOLE: no docstring

calls stdlib: builtins.open, json.loads, pathlib.Path
reads cross-module: scripts.code_map.extract:STATEMENTS_NAME
reads stdlib: json (module), pathlib (module)

referenced by: 3 sites, this module only
