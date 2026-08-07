# scripts.hooks.spine_rail:_same_path
function, scripts/hooks/spine_rail.py:309, 14 lines

```python
def _same_path(a, b) -> bool
```

True if a and b name the same path after normcase+normpath.

Fail-SAFE: on ANY exception return True. A comparison failure must never
spuriously relax the rail into treating a driving session as foreign.

calls stdlib: builtins.isinstance x2, os.path.normcase x2, os.path.normpath x2
reads stdlib: os (module) x4, os.path x4, builtins.str x2, builtins.Exception

referenced by: 1 sites, this module only
