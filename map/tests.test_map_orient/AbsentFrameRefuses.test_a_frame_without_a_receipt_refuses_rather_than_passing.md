# tests.test_map_orient:AbsentFrameRefuses.test_a_frame_without_a_receipt_refuses_rather_than_passing
method, tests/test_map_orient.py:761, 8 lines

```python
def test_a_frame_without_a_receipt_refuses_rather_than_passing(self)
```

No orientation happened at all -- the frame cannot be checked

against anything, and 'cannot check' is never 'passes'.

calls internal: AbsentFrameRefuses.assertEqual x2, RepoFixture, frame, verdict, verify_frame
reads internal: RepoFixture.root x2, GOOD_FRAME
unresolved: 1 reads (dispatch-unknown-base)

referenced by: none found
