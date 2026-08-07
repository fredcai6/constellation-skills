# tests.test_episode_store:ShippedStoreTests.test_the_real_tracked_store_is_readable_by_the_tooling_that_ships_with_it
method, tests/test_episode_store.py:2548, 24 lines

```python
def test_the_real_tracked_store_is_readable_by_the_tooling_that_ships_with_it(self)
```

Read-only, against the REAL `episodes/` — no temp store, nothing written.

This is the one-command check that was missing: does the thing being shipped
work? A store whose own placeholders are indistinguishable from episodes fails
here in a single line, three roles earlier than it otherwise would.

calls internal: ShippedStoreTests.assertIsNotNone x2, ShippedStoreTests.assertEqual
calls stdlib: builtins.str x2, json.loads, subprocess.run
reads internal: ROOT x2, QUERY_SCRIPT, ShippedStoreTests.m, ShippedStoreTests.q
reads stdlib: json (module), subprocess (module), sys (module), sys.executable
unresolved: 2 calls (dispatch-unknown-base), 4 reads (dispatch-unknown-base)

referenced by: none found
