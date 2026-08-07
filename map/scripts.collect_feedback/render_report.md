# scripts.collect_feedback:render_report
function, scripts/collect_feedback.py:587, 32 lines

```python
def render_report(new: Hits, open_unresolved: Hits) -> str
```

HOLE: no docstring

calls internal: _render_group x4
calls stdlib: builtins.len x6, datetime.date.today
reads internal: RECURRENCE_THRESHOLD x2
reads stdlib: datetime.date
unresolved: 9 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
