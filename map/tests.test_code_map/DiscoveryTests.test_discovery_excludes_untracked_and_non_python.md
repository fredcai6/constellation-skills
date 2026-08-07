# tests.test_code_map:DiscoveryTests.test_discovery_excludes_untracked_and_non_python
method, tests/test_code_map.py:85, 5 lines

```python
def test_discovery_excludes_untracked_and_non_python(self)
```

HOLE: no docstring

calls internal: DiscoveryTests.assertNotIn x2, DiscoveryTests.assertTrue
calls cross-module: scripts.code_map.discovery:discover_corpus
calls stdlib: builtins.all
reads internal: DiscoveryTests.repo
reads cross-module: scripts.code_map.discovery:
unresolved: 1 calls (dispatch-unknown-base)

referenced by: none found
