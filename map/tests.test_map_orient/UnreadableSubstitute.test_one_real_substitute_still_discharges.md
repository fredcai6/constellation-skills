# tests.test_map_orient:UnreadableSubstitute.test_one_real_substitute_still_discharges
method, tests/test_map_orient.py:498, 12 lines

```python
def test_one_real_substitute_still_discharges(self)
```

Positive control: the fix must not refuse a genuine declaration.

calls internal: UnreadableSubstitute.assertEqual x2, RepoFixture, RepoFixture.file, orient, verify
reads internal: RepoFixture.root x2
unresolved: 4 reads (dispatch-unknown-base)

referenced by: none found
