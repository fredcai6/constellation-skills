# scripts.hooks.spine_rail:resolve_project_dir
function, scripts/hooks/spine_rail.py:53, 2 lines

```python
def resolve_project_dir() -> Path
```

HOLE: no docstring

calls stdlib: os.environ.get, os.getcwd, pathlib.Path
reads stdlib: os (module) x2, os.environ

referenced by: 1 sites, this module only
