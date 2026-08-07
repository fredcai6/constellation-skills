# tests.test_map_orient:VerifyFrameContractShape.test_orient_never_prints_an_anchor_id
method, tests/test_map_orient.py:819, 19 lines

```python
def test_orient_never_prints_an_anchor_id(self)
```

LOAD-BEARING -- do not drop this test.

If `orient` echoed the ids it found, the citation check would be
self-satisfying: an agent could paste back what the tool told it and
never open the map. The proof that the map was read has to come from
somewhere the tool did not hand over.

calls internal: RepoFixture.file x2, VerifyFrameContractShape.assertEqual x2, RepoFixture, VerifyFrameContractShape.assertNotIn, VerifyFrameContractShape.subTest, orient, verdict
calls stdlib: builtins.hasattr
reads internal: mo x2, REAL_INDEX, REAL_PACKET, RepoFixture.root
unresolved: 1 calls (dispatch-unknown-base), 5 reads (dispatch-unknown-base)

referenced by: none found
