# tests.test_episode_store:WritePhaseAtomicityTests.test_forced_failure_on_second_of_two_writes_leaves_store_byte_for_byte_unchanged
method, tests/test_episode_store.py:472, 59 lines

```python
def test_forced_failure_on_second_of_two_writes_leaves_store_byte_for_byte_unchanged(self)
```

HOLE: no docstring

- [flaky_write](WritePhaseAtomicityTests.test_forced_failure_on_second_of_two_writes_leaves_store_byte_for_byte_unchanged.flaky_write.md) method: HOLE: no docstring

calls internal: WritePhaseAtomicityTests._snapshot x2, WritePhaseAtomicityTests.assertEqual x2, create_op x2, EpisodeStoreTestCase.run_delta, WritePhaseAtomicityTests.assertGreaterEqual
calls stdlib: builtins.str x2, json.dumps, pathlib.Path
reads internal: WritePhaseAtomicityTests.m x4, WritePhaseAtomicityTests.root, WritePhaseAtomicityTests.tmp
reads stdlib: json (module)
unresolved: 2 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base), 2 writes (dispatch-unknown-base)

referenced by: none found
