# tests.test_checklist_engine:GoldenOutputBriefing
class, tests/test_checklist_engine.py:3779, 93 lines

```python
class GoldenOutputBriefing(TestCase)
```

Golden-output tests for render_human()/current(): one per active-task

state (pending/in-progress/blocked) plus the three no-active-task branches
(DONE with no waived, DONE with WAIVED, survey ALL ITEMS VISITED). None of
these six had a golden (exact-output) test before this change, and they
are exactly the branches most likely to be silently reshaped by a
render_human() rewrite.

- [test_pending_active_task_shows_open_preconditions_and_next_start](GoldenOutputBriefing.test_pending_active_task_shows_open_preconditions_and_next_start.md) method: HOLE: no docstring
- [test_pending_active_task_with_satisfied_preconditions_shows_next_start](GoldenOutputBriefing.test_pending_active_task_with_satisfied_preconditions_shows_next_start.md) method: HOLE: no docstring
- [test_in_progress_active_task_shows_open_postconditions_and_next_advance](GoldenOutputBriefing.test_in_progress_active_task_shows_open_postconditions_and_next_advance.md) method: HOLE: no docstring
- [test_in_progress_non_exempt_with_open_command_postcondition_shows_advance_with_why](GoldenOutputBriefing.test_in_progress_non_exempt_with_open_command_postcondition_shows_advance_with_why.md) method: HOLE: no docstring
- [test_blocked_active_task_shows_resume_hint](GoldenOutputBriefing.test_blocked_active_task_shows_resume_hint.md) method: HOLE: no docstring
- [test_done_no_open_items_no_waived](GoldenOutputBriefing.test_done_no_open_items_no_waived.md) method: HOLE: no docstring
- [test_done_no_open_items_with_waived](GoldenOutputBriefing.test_done_no_open_items_with_waived.md) method: HOLE: no docstring
- [test_all_items_visited_prompts_consolidate](GoldenOutputBriefing.test_all_items_visited_prompts_consolidate.md) method: HOLE: no docstring

referenced by: none found
