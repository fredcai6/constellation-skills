# scripts.grade_lint:make_violation
function, scripts/grade_lint.py:159, 4 lines

```python
def make_violation(code: str, file: str, location, message: str) -> Violation
```

HOLE: no docstring

calls internal: Violation
calls stdlib: builtins.str
reads internal: CODE_INFO

referenced by: 16 sites, this module only
