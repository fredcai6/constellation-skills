# scripts.build_architecture_map:validate_map
function, scripts/build_architecture_map.py:274, 59 lines

```python
def validate_map(nodes: Sequence[dict[str, Any]], relationships: Sequence[dict[str, Any]]) -> list[str]
```

HOLE: no docstring

calls stdlib: builtins.set x2, builtins.sorted
reads internal: ALLOWED_CONFIDENCE x2, ALLOWED_LEVELS, ALLOWED_NODE_STATUS, ALLOWED_OVERLAY_KINDS, ALLOWED_RELATIONSHIPS
reads stdlib: builtins.str x3, builtins.set x2, builtins.list
unresolved: 35 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
