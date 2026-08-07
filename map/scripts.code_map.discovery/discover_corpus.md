# scripts.code_map.discovery:discover_corpus
function, scripts/code_map/discovery.py:33, 3 lines

```python
def discover_corpus(root)
```

The mappable corpus under `root`, as sorted posix-relative paths.

calls internal: is_mappable, tracked_python_files
calls stdlib: builtins.sorted

referenced by: 9 sites in 5 modules (scripts.code_map.checks, scripts.code_map.cli, scripts.code_map.extract, scripts.code_map.supplement, tests.test_code_map)
