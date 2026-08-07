# scripts.map_orient:_same_path
function, scripts/map_orient.py:346, 3 lines

```python
def _same_path(a: str, b: str) -> bool
```

PURE. Case- and separator-insensitive path identity (Windows-safe).

calls stdlib: os.path.normcase x2, os.path.normpath x2
reads stdlib: os (module) x4, os.path x4

referenced by: 1 sites, this module only
