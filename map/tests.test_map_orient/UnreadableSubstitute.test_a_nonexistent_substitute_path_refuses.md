# tests.test_map_orient:UnreadableSubstitute.test_a_nonexistent_substitute_path_refuses
method, tests/test_map_orient.py:464, 12 lines

```python
def test_a_nonexistent_substitute_path_refuses(self)
```

The reviewer's exact reproduction, pinned.

calls internal: UnreadableSubstitute.assertNotEqual x2, RepoFixture, UnreadableSubstitute.assertEqual, orient, verify
reads internal: RepoFixture.root x2
unresolved: 5 reads (dispatch-unknown-base)

referenced by: none found
