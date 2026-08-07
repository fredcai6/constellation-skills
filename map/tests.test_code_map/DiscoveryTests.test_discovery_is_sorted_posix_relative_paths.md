# tests.test_code_map:DiscoveryTests.test_discovery_is_sorted_posix_relative_paths
method, tests/test_code_map.py:91, 7 lines

```python
def test_discovery_is_sorted_posix_relative_paths(self)
```

HOLE: no docstring

calls internal: DiscoveryTests.assertEqual, DiscoveryTests.assertFalse, DiscoveryTests.assertNotIn, DiscoveryTests.assertTrue
calls cross-module: scripts.code_map.discovery:discover_corpus
calls stdlib: builtins.sorted, pathlib.Path
reads internal: DiscoveryTests.repo
reads cross-module: scripts.code_map.discovery:
unresolved: 1 calls (dispatch-unknown-base)

referenced by: none found
