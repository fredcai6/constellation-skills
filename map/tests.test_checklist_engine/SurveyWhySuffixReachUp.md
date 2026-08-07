# tests.test_checklist_engine:SurveyWhySuffixReachUp
class, tests/test_checklist_engine.py:3169, 29 lines

```python
class SurveyWhySuffixReachUp(TestCase)
```

#189 — `_why_suffix` is extended to surveys so a survey role (reviewer) can

cold-start from `current` alone. A survey never accumulates a `why_trail`, so no
`DIGEST:` line appears — only the `REFRESH REQUESTED:` line, the reach-up target.

- [test_survey_shows_no_refresh_line_before_attach](SurveyWhySuffixReachUp.test_survey_shows_no_refresh_line_before_attach.md) method: HOLE: no docstring
- [test_survey_refresh_request_renders_on_current](SurveyWhySuffixReachUp.test_survey_refresh_request_renders_on_current.md) method: HOLE: no docstring
- [test_survey_all_visited_renders_no_suffix](SurveyWhySuffixReachUp.test_survey_all_visited_renders_no_suffix.md) method: HOLE: no docstring

referenced by: none found
