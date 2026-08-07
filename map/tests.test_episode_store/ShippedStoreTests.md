# tests.test_episode_store:ShippedStoreTests
class, tests/test_episode_store.py:2504, 68 lines

```python
class ShippedStoreTests(QueryTestCase)
```

The tests that would have caught the g4 BLOCK, and the reason they did not exist.

Every other test in this file builds its own store and then reads it. Not one of them
read the store this repository actually SHIPS — so `episodes/active/README.md` and
`episodes/retired/README.md`, placed by this same gate, made the tracked store
unreadable by its own tooling while a green suite said otherwise. Two tests close
that gap from both ends: one reproduces the shipped store's real non-episode files in
a temp root and drives every primitive over it, and one runs the shipped CLI against
the real `episodes/` directory itself.

- [test_the_shipped_stores_own_placeholders_read_end_to_end](ShippedStoreTests.test_the_shipped_stores_own_placeholders_read_end_to_end.md) method: HOLE: no docstring
- [test_the_real_tracked_store_is_readable_by_the_tooling_that_ships_with_it](ShippedStoreTests.test_the_real_tracked_store_is_readable_by_the_tooling_that_ships_with_it.md) method: Read-only, against the REAL `episodes/` — no temp store, nothing written.

referenced by: none found
