# tests.test_code_map:DiscoveryTests
class, tests/test_code_map.py:58, 47 lines

```python
class DiscoveryTests(TestCase)
```

The discovery layer, against a synthetic repo — hermetic, so these do not

move when this repo's own file list moves.

- [setUp](DiscoveryTests.setUp.md) method: HOLE: no docstring
- [tearDown](DiscoveryTests.tearDown.md) method: HOLE: no docstring
- [test_discovery_excludes_agent_work](DiscoveryTests.test_discovery_excludes_agent_work.md) method: THE load-bearing one: remove the exclusion and this goes red.
- [test_discovery_excludes_untracked_and_non_python](DiscoveryTests.test_discovery_excludes_untracked_and_non_python.md) method: HOLE: no docstring
- [test_discovery_is_sorted_posix_relative_paths](DiscoveryTests.test_discovery_is_sorted_posix_relative_paths.md) method: HOLE: no docstring
- [test_discovery_predicate_and_listing_agree](DiscoveryTests.test_discovery_predicate_and_listing_agree.md) method: The corpus is defined by the predicate the module itself applies, not

referenced by: none found
