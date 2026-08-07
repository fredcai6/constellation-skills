# scripts.build_architecture_map:parse_packet
function, scripts/build_architecture_map.py:78, 57 lines

```python
def parse_packet(packet: Path, repo_root: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]
```

HOLE: no docstring

calls internal: required_field x4, normalize_value, repo_path
calls stdlib: re.compile x2
reads stdlib: builtins.str x4, builtins.dict x2, re (module) x2, builtins.list, typing.Any
unresolved: 23 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
