# scripts.apply_lessons_delta:apply_delta
function, scripts/apply_lessons_delta.py:425, 220 lines

```python
def apply_delta(book: Playbook, delta: dict) -> list[str]
```

HOLE: no docstring

calls internal: LessonsDeltaError x8, _stamp_date x3, Lesson, Playbook.find, _apply_threshold_ripe, _is_doctrine_target, _stamp, validate_delta
calls stdlib: builtins.str x15, builtins.sorted
reads internal: Playbook.active x5, Playbook.dormancy_runs x2, Playbook.run_tick x2, Playbook.ticked_work_ids x2, Lesson, TICKED_WORK_ID_RETENTION
reads stdlib: builtins.list x2, builtins.str
writes internal: Playbook.run_tick, Playbook.ticked_work_ids
unresolved: 4 calls (chained-attribute), 50 calls (dispatch-unknown-base), 42 reads (dispatch-unknown-base), 20 writes (dispatch-unknown-base)

referenced by: 1 sites, this module only
