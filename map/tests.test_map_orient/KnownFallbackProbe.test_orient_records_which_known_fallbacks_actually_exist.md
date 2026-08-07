# tests.test_map_orient:KnownFallbackProbe.test_orient_records_which_known_fallbacks_actually_exist
method, tests/test_map_orient.py:909, 12 lines

```python
def test_orient_records_which_known_fallbacks_actually_exist(self)
```

Existence is settled by the filesystem, not by the agent's account.

calls internal: KnownFallbackProbe.assertTrue x2, RepoFixture.file x2, KnownFallbackProbe.assertEqual, KnownFallbackProbe.assertFalse, RepoFixture, orient, receipt_of
calls stdlib: builtins.tuple
reads internal: RepoFixture.root x2, mo
unresolved: 1 reads (dispatch-unknown-base)

referenced by: none found
