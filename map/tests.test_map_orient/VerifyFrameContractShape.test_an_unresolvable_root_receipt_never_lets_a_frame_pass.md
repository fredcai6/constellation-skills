# tests.test_map_orient:VerifyFrameContractShape.test_an_unresolvable_root_receipt_never_lets_a_frame_pass
method, tests/test_map_orient.py:874, 6 lines

```python
def test_an_unresolvable_root_receipt_never_lets_a_frame_pass(self)
```

HOLE: no docstring

calls internal: RepoFixture, VerifyFrameContractShape.assertEqual, degraded_receipt, frame, verify_frame
reads internal: RepoFixture.root x3, GOOD_FRAME
unresolved: 1 reads (dispatch-unknown-base)

referenced by: none found
