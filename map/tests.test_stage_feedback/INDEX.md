# tests.test_stage_feedback
tests/test_stage_feedback.py, 259 lines, 18 holes

HOLE: no docstring

imports stdlib: importlib.util, json, pathlib.Path, tempfile, unittest
imported by: none found

```python
ROOT = Path(__file__).resolve().parents[1]
SAMPLE_BODY = "**Run shape:** `commander (delegated)` · spine init->archive\n\n**Instruction adherenc...
```

- [_load](_load.md) function: HOLE: no docstring
- [load_stage_feedback](load_stage_feedback.md) function: HOLE: no docstring
- [load_verify_agent_feedback](load_verify_agent_feedback.md) function: HOLE: no docstring
- [StageFeedbackTests](StageFeedbackTests.md) class: HOLE: no docstring
  - [StageFeedbackTests.test_writes_all_four_files](StageFeedbackTests.test_writes_all_four_files.md) method: HOLE: no docstring
  - [StageFeedbackTests.test_agent_feedback_heading_carries_work_id](StageFeedbackTests.test_agent_feedback_heading_carries_work_id.md) method: HOLE: no docstring
  - [StageFeedbackTests.test_default_lessons_delta_is_tick_only_valid_json](StageFeedbackTests.test_default_lessons_delta_is_tick_only_valid_json.md) method: HOLE: no docstring
  - [StageFeedbackTests.test_invalid_lessons_delta_json_rejected](StageFeedbackTests.test_invalid_lessons_delta_json_rejected.md) method: HOLE: no docstring
  - [StageFeedbackTests.test_default_constellation_feedback_confirms_empty](StageFeedbackTests.test_default_constellation_feedback_confirms_empty.md) method: HOLE: no docstring
  - [StageFeedbackTests.test_fence_cites_launch_order_ownership_and_return_shape](StageFeedbackTests.test_fence_cites_launch_order_ownership_and_return_shape.md) method: HOLE: no docstring
  - [StageFeedbackTests.test_no_clobber_without_force](StageFeedbackTests.test_no_clobber_without_force.md) method: HOLE: no docstring
  - [StageFeedbackTests.test_force_overwrites](StageFeedbackTests.test_force_overwrites.md) method: HOLE: no docstring
  - [StageFeedbackTests.test_empty_fence_text_rejected](StageFeedbackTests.test_empty_fence_text_rejected.md) method: HOLE: no docstring
- [VerifyAgentFeedbackAcceptsStagedOutputTests](VerifyAgentFeedbackAcceptsStagedOutputTests.md) class: The whole point of the script: what it writes must pass
  - [VerifyAgentFeedbackAcceptsStagedOutputTests._stage](VerifyAgentFeedbackAcceptsStagedOutputTests._stage.md) method: HOLE: no docstring
  - [VerifyAgentFeedbackAcceptsStagedOutputTests.test_phase_feedback_passes_against_staged_output](VerifyAgentFeedbackAcceptsStagedOutputTests.test_phase_feedback_passes_against_staged_output.md) method: HOLE: no docstring
  - [VerifyAgentFeedbackAcceptsStagedOutputTests.test_phase_archive_passes_when_work_area_already_swept](VerifyAgentFeedbackAcceptsStagedOutputTests.test_phase_archive_passes_when_work_area_already_swept.md) method: HOLE: no docstring
  - [VerifyAgentFeedbackAcceptsStagedOutputTests.test_missing_member_of_trio_still_fails](VerifyAgentFeedbackAcceptsStagedOutputTests.test_missing_member_of_trio_still_fails.md) method: HOLE: no docstring
  - [VerifyAgentFeedbackAcceptsStagedOutputTests.test_boilerplate_only_feedback_body_still_fails](VerifyAgentFeedbackAcceptsStagedOutputTests.test_boilerplate_only_feedback_body_still_fails.md) method: HOLE: no docstring
