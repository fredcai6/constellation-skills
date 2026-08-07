# tests.test_map_orient:VerifyFrameContractShape.test_report_only_is_the_flag_flip_between_gating_and_reporting
method, tests/test_map_orient.py:881, 11 lines

```python
def test_report_only_is_the_flag_flip_between_gating_and_reporting(self)
```

The gate-vs-report ruling must be a flag flip, not a rebuild -- and

the reported verdict must be unchanged, only its blocking-ness.

calls internal: VerifyFrameContractShape.assertEqual x2, verdict x2, verify_frame x2, VerifyFrameContractShape.assertIn, VerifyFrameContractShape.assertNotEqual, frame, resolved_repo
reads internal: CODE_CUT_FRAME
unresolved: 6 reads (dispatch-unknown-base)

referenced by: none found
