# scripts.grade_lint:compute_exit_code
function, scripts/grade_lint.py:672, 6 lines

```python
def compute_exit_code(violations: list[Violation], strict_warnings: bool) -> int
```

HOLE: no docstring

calls stdlib: builtins.any x2
reads internal: FAIL, WARN
unresolved: 2 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
