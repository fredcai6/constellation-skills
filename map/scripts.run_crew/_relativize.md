# scripts.run_crew:_relativize
function, scripts/run_crew.py:297, 10 lines

```python
def _relativize(path: str, root: Path) -> str
```

Store paths in the registry relative to root when possible (matches the

issue's example shape), else verbatim.

calls stdlib: pathlib.Path
reads stdlib: builtins.ValueError
unresolved: 6 calls (dispatch-unknown-base)

referenced by: 4 sites, this module only
