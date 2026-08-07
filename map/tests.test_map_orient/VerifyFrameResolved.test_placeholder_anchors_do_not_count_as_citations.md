# tests.test_map_orient:VerifyFrameResolved.test_placeholder_anchors_do_not_count_as_citations
method, tests/test_map_orient.py:802, 5 lines

```python
def test_placeholder_anchors_do_not_count_as_citations(self)
```

An unfilled MISSION_FRAME scaffold must not satisfy the check.

calls internal: VerifyFrameResolved.assertNotEqual, frame, resolved_repo, verify_frame
unresolved: 3 reads (dispatch-unknown-base)

referenced by: none found
