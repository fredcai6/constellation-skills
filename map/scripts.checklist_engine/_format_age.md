# scripts.checklist_engine:_format_age
function, scripts/checklist_engine.py:1252, 19 lines

```python
def _format_age(delta: timedelta) -> str
```

Render a timedelta as whole seconds/minutes/hours — pure arithmetic and

string formatting only, NO threshold comparisons (constraint:no-threshold-
values): the unit boundaries below (60s/min, 3600s/hr) are unit-conversion
arithmetic, not a judgment call on whether an age is "old" — this function
never decides that, it only renders whatever age it is handed. A negative
delta (a caller passing a future observed_at) clamps to 0s rather than
printing a negative age.

calls stdlib: builtins.divmod x2, builtins.int
unresolved: 1 calls (dispatch-unknown-base)

referenced by: 2 sites, this module only
