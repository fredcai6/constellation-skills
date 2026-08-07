# scripts.build_architecture_map:build_architecture_map
function, scripts/build_architecture_map.py:335, 52 lines

```python
def build_architecture_map(repo_root: str | Path, *, source_roots: Sequence[str] = ('src',), write_output: bool = True) -> BuildResult
```

HOLE: no docstring

calls internal: BuildResult, MapBuildError, parse_overlay, parse_packet, scan_source_tree, validate_map
calls stdlib: builtins.sorted x5, json.dumps, pathlib.Path
reads stdlib: builtins.dict x3, builtins.list x3, builtins.str x3, typing.Any x3, json (module)
unresolved: 19 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base), 6 reads (unbound-name)

referenced by: 1 sites, this module only
