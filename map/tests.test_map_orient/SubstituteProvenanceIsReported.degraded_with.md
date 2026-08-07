# tests.test_map_orient:SubstituteProvenanceIsReported.degraded_with
method, tests/test_map_orient.py:1053, 11 lines

```python
def degraded_with(self, files: dict, *substitutes: str) -> subprocess.CompletedProcess
```

Orient a mapless repo declaring `substitutes`, then report on it.

calls internal: RepoFixture, RepoFixture.file, orient, verify
reads internal: RepoFixture.root x2
unresolved: 1 calls (dispatch-unknown-base)

referenced by: 4 sites, this module only
