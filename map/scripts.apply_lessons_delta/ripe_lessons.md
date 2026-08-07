# scripts.apply_lessons_delta:ripe_lessons
function, scripts/apply_lessons_delta.py:290, 25 lines

```python
def ripe_lessons(book: Playbook) -> list[Lesson]
```

Threshold-ripe lessons still awaiting an apply/export/defer disposition.

reads internal: Lesson, Playbook.active, Playbook.apply_confirmed, Playbook.apply_recurrences
reads stdlib: builtins.list
unresolved: 1 calls (dispatch-unknown-base), 10 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
