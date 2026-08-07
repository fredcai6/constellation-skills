# tests.test_episode_store:AllOrNothingAtomicTests
class, tests/test_episode_store.py:415, 40 lines

```python
class AllOrNothingAtomicTests(EpisodeStoreTestCase)
```

C4 — an invalid op ANYWHERE in a multi-op delta leaves the store byte-for-byte

unchanged, even when an earlier op in the same delta is individually valid and
would, on its own, have mutated a file.

- [test_atomic_invalid_op_in_multi_op_delta_leaves_files_unchanged](AllOrNothingAtomicTests.test_atomic_invalid_op_in_multi_op_delta_leaves_files_unchanged.md) method: HOLE: no docstring
- [test_atomic_structurally_invalid_op_in_multi_op_delta_also_leaves_files_unchanged](AllOrNothingAtomicTests.test_atomic_structurally_invalid_op_in_multi_op_delta_also_leaves_files_unchanged.md) method: HOLE: no docstring

referenced by: none found
