# tests.test_map_orient:VerifyFrameResolved.test_the_shipped_mission_frame_template_itself_does_not_pass
method, tests/test_map_orient.py:808, 8 lines

```python
def test_the_shipped_mission_frame_template_itself_does_not_pass(self)
```

The scaffold this repo ships, verbatim. Uses the real committed file

so it cannot rot into a fixture nobody maintains.

calls internal: VerifyFrameResolved.assertNotEqual, VerifyFrameResolved.assertTrue, frame, resolved_repo, verify_frame
reads internal: ROOT
unresolved: 2 calls (dispatch-unknown-base), 3 reads (dispatch-unknown-base)

referenced by: none found
