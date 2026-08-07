# tests.test_apply_lessons_delta:ApplyLessonsDeltaTests._confirm
method, tests/test_apply_lessons_delta.py:250, 11 lines

```python
def _confirm(self, n_or_lesson_id, work_id_or_lid='handoff-diff-command', grounding='it recurred again')
```

Support both old signature (lesson_id, work_id) and new signature (n, lid).

calls internal: ApplyLessonsDeltaTests.run_delta x2
calls stdlib: builtins.isinstance, builtins.range
reads stdlib: builtins.int

referenced by: 16 sites, this module only
