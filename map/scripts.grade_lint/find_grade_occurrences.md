# scripts.grade_lint:find_grade_occurrences
function, scripts/grade_lint.py:170, 14 lines

```python
def find_grade_occurrences(text: str) -> list[str]
```

Every literal '@grade:' occurrence's body in `text`, each bounded by the

next occurrence (or end of string). A trailing backtick closing a
backtick-wrapped tag is stripped. Returns [] when no occurrence exists.

calls stdlib: builtins.len x3, builtins.enumerate, re.escape, re.finditer
reads internal: GRADE_MARKER x2
reads stdlib: re (module) x2
unresolved: 5 calls (dispatch-unknown-base)

referenced by: 5 sites, this module only
