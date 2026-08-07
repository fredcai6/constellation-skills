# tests.test_map_orient:VerifyFrameDegraded.test_a_degraded_frame_citing_map_anchors_refuses
method, tests/test_map_orient.py:1025, 5 lines

```python
def test_a_degraded_frame_citing_map_anchors_refuses(self)
```

No map was read, so a map anchor cannot be a member of anything.

calls internal: VerifyFrameDegraded.assertNotEqual, VerifyFrameDegraded.degraded_repo, frame, verify_frame
reads internal: GOOD_FRAME
unresolved: 3 reads (dispatch-unknown-base)

referenced by: none found
