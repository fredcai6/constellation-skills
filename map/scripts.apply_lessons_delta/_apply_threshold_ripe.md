# scripts.apply_lessons_delta:_apply_threshold_ripe
function, scripts/apply_lessons_delta.py:317, 9 lines

```python
def _apply_threshold_ripe(book: Playbook, lesson: Lesson) -> bool
```

Is this non-constellation lesson ripe for apply?

Apply only ever reaches non-constellation lessons (constellation is refused
earlier in the apply branch), so ripeness here is `confirmed >= apply_confirmed`
— the same threshold `ripe_lessons()` uses for non-constellation lessons.
Single source of the number; do not fork it.

reads internal: Lesson.confirmed, Playbook.apply_confirmed

referenced by: 1 sites, this module only
