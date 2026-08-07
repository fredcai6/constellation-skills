# scripts.code_map.render:repo_name
function, scripts/code_map/render.py:348, 18 lines

```python
def repo_name(root)
```

Name the map after the repository, not the directory it was built in: a

git worktree's directory is named for the branch, so `<root>.name` would
title the map after whatever scratch checkout happened to build it.

calls stdlib: pathlib.Path x2, builtins.str, subprocess.run
reads stdlib: pathlib (module) x2, builtins.Exception, subprocess (module)
writes internal: repo_name.root
unresolved: 4 calls (dispatch-unknown-base), 6 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
