# src.utils.simplification_limits:iter_python_files
function, src/utils/simplification_limits.py:77, 26 lines

```python
def iter_python_files(roots: Sequence[str | Path], *, project_root: Path = PROJECT_ROOT, extra_paths: Optional[Sequence[str | Path]] = None) -> List[Path]
```

HOLE: no docstring

calls internal: _is_excluded_path
calls stdlib: builtins.list x2, builtins.sorted x2, builtins.set, pathlib.Path
reads stdlib: pathlib.Path x2, builtins.set, typing.List
unresolved: 7 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
