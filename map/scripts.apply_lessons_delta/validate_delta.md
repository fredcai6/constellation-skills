# scripts.apply_lessons_delta:validate_delta
function, scripts/apply_lessons_delta.py:349, 74 lines

```python
def validate_delta(delta: dict) -> tuple[str, bool, list[dict]]
```

HOLE: no docstring

calls internal: LessonsDeltaError x18
calls stdlib: builtins.str x10, builtins.isinstance x2, builtins.any, builtins.bool, re.fullmatch, re.search
reads internal: SCOPES x4
reads stdlib: re (module) x2, builtins.list, builtins.str
unresolved: 29 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
