# tests.test_code_map:_make_repo
function, tests/test_code_map.py:41, 15 lines

```python
def _make_repo(tmp: Path)
```

A synthetic git repo whose tracked set spans every case the filter sees:

a source file, a run-scratch file under .agent-work/, a nested scratch file,
a tracked non-Python file, and an untracked Python file.

calls internal: _git x2
unresolved: 8 calls (dispatch-unknown-base)

referenced by: 3 sites, this module only
