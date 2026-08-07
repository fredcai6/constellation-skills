# tests.test_map_orient:VerifyOrientation.test_an_unresolvable_root_receipt_never_passes
method, tests/test_map_orient.py:548, 6 lines

```python
def test_an_unresolvable_root_receipt_never_passes(self)
```

HOLE: no docstring

calls internal: VerifyOrientation.assertEqual x2, RepoFixture, degraded_receipt, verdict, verify
reads internal: RepoFixture.root x2
unresolved: 1 reads (dispatch-unknown-base)

referenced by: none found
