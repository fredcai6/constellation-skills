# tests.test_episode_store:HalfRetirementSafetyTests._sets
method, tests/test_episode_store.py:1973, 8 lines

```python
def _sets(self)
```

(ordinary-set ids, archive ids) read straight off the filesystem, without

going through the code under test — otherwise a bug in the seams could hide
itself from the very assertion meant to catch it.

calls stdlib: builtins.sorted x2
reads internal: HalfRetirementSafetyTests.root x2
unresolved: 2 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
