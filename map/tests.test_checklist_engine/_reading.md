# tests.test_checklist_engine:_reading
function, tests/test_checklist_engine.py:3204, 8 lines

```python
def _reading(fill, model='claude-opus-4-8')
```

A fresh, well-formed gauge Reading with the given fill — constructed

directly so band-structure tests are decoupled from the reader's file I/O
and clock. `observed_at` is aware `now` (the field is unused by the policy).

calls stdlib: datetime.datetime.now
reads internal: E
reads stdlib: datetime.datetime, datetime.timezone, datetime.timezone.utc
unresolved: 1 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: 11 sites, this module only
