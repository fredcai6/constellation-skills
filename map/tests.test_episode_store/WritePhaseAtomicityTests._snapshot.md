# tests.test_episode_store:WritePhaseAtomicityTests._snapshot
method, tests/test_episode_store.py:466, 5 lines

```python
def _snapshot(self)
```

Every file under the store root, by path, as raw bytes -- content AND

the exact set of files present, so a stray leftover temp/staged file would
also be caught, not just a content mismatch on an existing file.

calls stdlib: builtins.sorted
reads internal: WritePhaseAtomicityTests.root
unresolved: 3 calls (dispatch-unknown-base)

referenced by: 2 sites, this module only
