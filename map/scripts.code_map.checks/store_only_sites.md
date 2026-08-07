# scripts.code_map.checks:store_only_sites
function, scripts/code_map/checks.py:130, 20 lines

```python
def store_only_sites(root, supp, artifacts)
```

What the store sees that the supplement's body-walk does not.

calls internal: _statements
calls stdlib: builtins.print x3, builtins.len, builtins.max, builtins.sorted, pathlib.Path
reads stdlib: builtins.Exception, pathlib (module)
writes internal: store_only_sites.root
unresolved: 7 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
