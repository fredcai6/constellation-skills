# tests.test_code_map:DiscoveryOnThisRepoTests.test_discovery_on_this_repo_excludes_agent_work
method, tests/test_code_map.py:112, 9 lines

```python
def test_discovery_on_this_repo_excludes_agent_work(self)
```

HOLE: no docstring

calls internal: DiscoveryOnThisRepoTests.assertTrue x2, DiscoveryOnThisRepoTests.assertEqual, DiscoveryOnThisRepoTests.assertIn
calls cross-module: scripts.code_map.discovery:discover_corpus, scripts.code_map.discovery:tracked_python_files
reads internal: ROOT x2
reads cross-module: scripts.code_map.discovery: x2
unresolved: 2 calls (dispatch-unknown-base)

referenced by: none found
