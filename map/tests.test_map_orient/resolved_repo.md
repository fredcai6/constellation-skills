# tests.test_map_orient:resolved_repo
function, tests/test_map_orient.py:717, 7 lines

```python
def resolved_repo(case: unittest.TestCase) -> RepoFixture
```

A repo with a real map, already oriented -- the RESOLVED baseline.

calls internal: RepoFixture, RepoFixture.file, orient
reads internal: REAL_INDEX, RepoFixture.root
unresolved: 1 calls (dispatch-unknown-base), 3 reads (dispatch-unknown-base)

referenced by: 13 sites, this module only
