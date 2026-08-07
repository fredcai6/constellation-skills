# scripts.build_architecture_map:scan_source_tree
function, scripts/build_architecture_map.py:222, 50 lines

```python
def scan_source_tree(repo_root: Path, source_roots: Iterable[str]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]
```

HOLE: no docstring

calls internal: module_node_id
calls stdlib: builtins.any, builtins.sorted
reads internal: SOURCE_SUFFIXES
reads stdlib: builtins.dict x2, builtins.list x2, builtins.str x2, typing.Any x2
unresolved: 12 calls (dispatch-unknown-base), 3 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
