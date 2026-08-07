# scripts.code_map.discovery:tracked_python_files
function, scripts/code_map/discovery.py:24, 7 lines

```python
def tracked_python_files(root)
```

Every Python file git tracks under `root`, as sorted posix-relative paths.

calls stdlib: builtins.sorted, builtins.str, subprocess.run
reads stdlib: subprocess (module)
unresolved: 1 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: 4 sites in 2 modules (tests.test_code_map)
