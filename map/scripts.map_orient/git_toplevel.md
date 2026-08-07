# scripts.map_orient:git_toplevel
function, scripts/map_orient.py:1006, 14 lines

```python
def git_toplevel(root: Path) -> str | None
```

`git -C <root> rev-parse --show-toplevel`, or None when it cannot answer.

calls stdlib: builtins.str, subprocess.run
reads stdlib: subprocess (module) x2, builtins.OSError, subprocess.SubprocessError
unresolved: 1 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
