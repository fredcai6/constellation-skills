# tests.test_episode_store:WritePhaseAtomicityTests
class, tests/test_episode_store.py:457, 74 lines

```python
class WritePhaseAtomicityTests(EpisodeStoreTestCase)
```

REWORK (g2 review BLOCK, defect 2): AllOrNothingAtomicTests above proves

all-or-nothing holds for every VALIDATION-time failure (a bad op anywhere in the
delta). This class proves it also holds for a real OS-level failure DURING the
write phase itself -- disk full, permission denied, a locked file -- which the
old _Transaction.commit() (sequential path.write_text() per touched file, no
staging) did not guarantee: a failure on the 2nd of 2 writes left the 1st file's
write landed on disk.

- [_snapshot](WritePhaseAtomicityTests._snapshot.md) method: Every file under the store root, by path, as raw bytes -- content AND
- [test_forced_failure_on_second_of_two_writes_leaves_store_byte_for_byte_unchanged](WritePhaseAtomicityTests.test_forced_failure_on_second_of_two_writes_leaves_store_byte_for_byte_unchanged.md) method: HOLE: no docstring

referenced by: none found
