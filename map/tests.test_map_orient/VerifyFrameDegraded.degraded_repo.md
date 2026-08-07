# tests.test_map_orient:VerifyFrameDegraded.degraded_repo
method, tests/test_map_orient.py:997, 10 lines

```python
def degraded_repo(self, *extra_files: str) -> RepoFixture
```

HOLE: no docstring

calls internal: RepoFixture.file x2, RepoFixture, VerifyFrameDegraded.assertTrue, orient, verdict
reads internal: RepoFixture.root
unresolved: 1 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: 4 sites, this module only
