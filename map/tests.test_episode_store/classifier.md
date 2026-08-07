# tests.test_episode_store:classifier
function, tests/test_episode_store.py:69, 13 lines

```python
def classifier()
```

The store's own episode classifier (`episode_id_for`), loaded once.

Tests ask the SHIPPED classifier "is this file an episode?" rather than answering it
themselves. The g4 review found the opposite in this file — two helpers each carrying
an inline comparison of `p.name` against the literal README filename — and that
hand-filtering is exactly why no test
could see that the shipped store's own placeholders were being minted into a phantom
episode id. A test that re-implements the predicate under test is testing itself.

calls internal: load

referenced by: 4 sites, this module only
