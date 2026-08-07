# scripts.grade_lint:Violation
class, scripts/grade_lint.py:150, 7 lines

```python
@dataclass
class Violation
```

HOLE: no docstring

```python
code: str
name: str
severity: str
file: str
location: str
message: str
```

reads stdlib: builtins.str x6
writes internal: Violation.code, Violation.file, Violation.location, Violation.message, Violation.name, Violation.severity

referenced by: 17 sites, this module only
