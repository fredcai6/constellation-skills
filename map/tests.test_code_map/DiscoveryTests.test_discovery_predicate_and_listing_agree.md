# tests.test_code_map:DiscoveryTests.test_discovery_predicate_and_listing_agree
method, tests/test_code_map.py:99, 6 lines

```python
def test_discovery_predicate_and_listing_agree(self)
```

The corpus is defined by the predicate the module itself applies, not

by a second hand-maintained list that can drift from it.

calls internal: DiscoveryTests.assertEqual
calls cross-module: scripts.code_map.discovery:discover_corpus, scripts.code_map.discovery:is_mappable, scripts.code_map.discovery:tracked_python_files
calls stdlib: builtins.sorted
reads internal: DiscoveryTests.repo x2
reads cross-module: scripts.code_map.discovery: x3

referenced by: none found
