# tests.test_episode_store:AbsentStoreTests
class, tests/test_episode_store.py:2431, 71 lines

```python
class AbsentStoreTests(QueryTestCase)
```

Trap 5 — a store that is not there is REFUSED, never answered as empty.

`Path.glob` over a missing directory returns nothing, so the naive reading of an
absent store root is `count: 0, exit 0` — which is trap 1's own failure description
("an empty candidate set is indistinguishable from 'the store is empty'") arriving
through a typo'd `--store-root` instead of through a wrong glob. It matters more
after the layout was bound than before it: the store now REQUIRES two subdirectories,
and git does not track empty directories, so "the layout never got committed" is a
real way to arrive here.

The writer is the deliberate exception: writing is a creating act, so it bootstraps
the layout. Reading is not, so no read seam ever creates anything.

- [test_a_store_root_that_does_not_exist_is_refused](AbsentStoreTests.test_a_store_root_that_does_not_exist_is_refused.md) method: HOLE: no docstring
- [test_a_missing_layout_directory_is_refused_rather_than_read_as_empty](AbsentStoreTests.test_a_missing_layout_directory_is_refused_rather_than_read_as_empty.md) method: HOLE: no docstring
- [test_a_reader_never_creates_the_store_it_could_not_find](AbsentStoreTests.test_a_reader_never_creates_the_store_it_could_not_find.md) method: HOLE: no docstring
- [test_the_writer_bootstraps_a_brand_new_store_root](AbsentStoreTests.test_the_writer_bootstraps_a_brand_new_store_root.md) method: The other half of the rule: a create into a store root that does not exist yet

referenced by: none found
