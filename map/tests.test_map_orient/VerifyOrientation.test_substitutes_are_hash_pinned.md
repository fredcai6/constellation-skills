# tests.test_map_orient:VerifyOrientation.test_substitutes_are_hash_pinned
method, tests/test_map_orient.py:568, 12 lines

```python
def test_substitutes_are_hash_pinned(self)
```

HOLE: no docstring

calls internal: VerifyOrientation.assertEqual x2, RepoFixture, RepoFixture.file, orient, receipt_of
calls stdlib: hashlib.sha256
reads internal: RepoFixture.root x2
reads stdlib: hashlib (module)
unresolved: 2 calls (dispatch-unknown-base)

referenced by: none found
