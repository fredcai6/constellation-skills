# scripts.build_architecture_map:parse_overlay
function, scripts/build_architecture_map.py:144, 70 lines

```python
def parse_overlay(path: Path, repo_root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]
```

HOLE: no docstring

- [flush](parse_overlay.flush.md) method: HOLE: no docstring

calls internal: parse_overlay_value x3
calls stdlib: builtins.len x2
reads stdlib: builtins.str x4, builtins.dict x3, typing.Any x3, builtins.list x2
unresolved: 17 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
