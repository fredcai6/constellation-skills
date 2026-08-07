# scripts.grade_lint:violation_to_dict
function, scripts/grade_lint.py:680, 3 lines

```python
def violation_to_dict(v: Violation) -> dict
```

HOLE: no docstring

reads internal: Violation.code, Violation.file, Violation.location, Violation.message, Violation.name, Violation.severity

referenced by: 1 sites, this module only
