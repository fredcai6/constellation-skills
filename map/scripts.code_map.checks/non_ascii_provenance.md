# scripts.code_map.checks:non_ascii_provenance
function, scripts/code_map/checks.py:38, 45 lines

```python
def non_ascii_provenance(supp, out)
```

(b) every non-ASCII line in the page tree should trace to a docstring or

a source value the renderer copied through.

calls stdlib: builtins.print x5, builtins.any x2, builtins.len x2, builtins.str x2, builtins.ascii, builtins.enumerate, builtins.ord, builtins.set, builtins.sorted, pathlib.Path
reads stdlib: pathlib (module)
unresolved: 30 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
