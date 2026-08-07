# tests.test_verify_agent_feedback
tests/test_verify_agent_feedback.py, 171 lines, 18 holes

HOLE: no docstring

imports stdlib: importlib.util, pathlib.Path, tempfile, unittest
imported by: none found

```python
ROOT = Path(__file__).resolve().parents[1]
REAL_ENTRY = '# Agent Feedback Log\n\n## 2026-06-10 — issue-9\n\n**Run shape:** commander · 2 gates ...
BOILERPLATE_ENTRY = '# Agent Feedback Log\n\n## 2026-06-10 — issue-9\n\n**Instruction adherence:** fully fo...
REASONED_NONE_ENTRY = BOILERPLATE_ENTRY.replace('- none', '- none — confirmed after review: reread each hando...
```

- [load](load.md) function: HOLE: no docstring
- [VerifyAgentFeedbackTests](VerifyAgentFeedbackTests.md) class: HOLE: no docstring
  - [VerifyAgentFeedbackTests.setUp](VerifyAgentFeedbackTests.setUp.md) method: HOLE: no docstring
  - [VerifyAgentFeedbackTests.tearDown](VerifyAgentFeedbackTests.tearDown.md) method: HOLE: no docstring
  - [VerifyAgentFeedbackTests.write_log](VerifyAgentFeedbackTests.write_log.md) method: HOLE: no docstring
  - [VerifyAgentFeedbackTests.verify](VerifyAgentFeedbackTests.verify.md) method: HOLE: no docstring
  - [VerifyAgentFeedbackTests.test_real_entry_passes](VerifyAgentFeedbackTests.test_real_entry_passes.md) method: HOLE: no docstring
  - [VerifyAgentFeedbackTests.test_missing_log_fails](VerifyAgentFeedbackTests.test_missing_log_fails.md) method: HOLE: no docstring
  - [VerifyAgentFeedbackTests.test_boilerplate_all_none_fails](VerifyAgentFeedbackTests.test_boilerplate_all_none_fails.md) method: HOLE: no docstring
  - [VerifyAgentFeedbackTests.test_reasoned_none_passes](VerifyAgentFeedbackTests.test_reasoned_none_passes.md) method: HOLE: no docstring
  - [VerifyAgentFeedbackTests.test_lessons_in_work_area_fails](VerifyAgentFeedbackTests.test_lessons_in_work_area_fails.md) method: HOLE: no docstring
  - [VerifyAgentFeedbackTests.test_archived_lessons_fails](VerifyAgentFeedbackTests.test_archived_lessons_fails.md) method: HOLE: no docstring
  - [VerifyAgentFeedbackTests.test_archive_phase_passes_when_clean](VerifyAgentFeedbackTests.test_archive_phase_passes_when_clean.md) method: HOLE: no docstring
  - [VerifyAgentFeedbackTests.stage_trio](VerifyAgentFeedbackTests.stage_trio.md) method: HOLE: no docstring
  - [VerifyAgentFeedbackTests.test_fenced_staged_trio_passes](VerifyAgentFeedbackTests.test_fenced_staged_trio_passes.md) method: HOLE: no docstring
  - [VerifyAgentFeedbackTests.test_fence_citation_without_trio_fails](VerifyAgentFeedbackTests.test_fence_citation_without_trio_fails.md) method: HOLE: no docstring
  - [VerifyAgentFeedbackTests.test_unfenced_missing_log_unchanged](VerifyAgentFeedbackTests.test_unfenced_missing_log_unchanged.md) method: HOLE: no docstring
  - [VerifyAgentFeedbackTests.test_unfenced_durable_still_passes_ignores_staged](VerifyAgentFeedbackTests.test_unfenced_durable_still_passes_ignores_staged.md) method: HOLE: no docstring
