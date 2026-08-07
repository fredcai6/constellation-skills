# scripts.checklist_engine:_glob_match
function, scripts/checklist_engine.py:523, 15 lines

```python
def _glob_match(path: str, pattern: str) -> bool
```

Match a POSIX-style path against a glob pattern with recursive `**`.

We normalize to forward slashes so Windows-style paths still match. A bare
basename pattern like `*.parquet` matches on any segment (it is also tried
against the final path component) so `sub/dir/x.parquet` is caught.

calls internal: _glob_to_regex
calls stdlib: re.match x2, builtins.bool
reads stdlib: re (module) x2
unresolved: 2 calls (dispatch-unknown-base)

referenced by: 2 sites, this module only
