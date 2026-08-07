# tests.test_code_map:DiscoveryTests.test_discovery_excludes_agent_work
method, tests/test_code_map.py:70, 14 lines

```python
def test_discovery_excludes_agent_work(self)
```

THE load-bearing one: remove the exclusion and this goes red.

calls internal: DiscoveryTests.assertEqual x4
calls cross-module: scripts.code_map.discovery:discover_corpus, scripts.code_map.discovery:tracked_python_files
calls stdlib: builtins.len x3, builtins.sorted
reads internal: DiscoveryTests.repo x2
reads cross-module: scripts.code_map.discovery: x2
unresolved: 2 calls (dispatch-unknown-base)

referenced by: none found
