# scripts.grade_lint:DecisionRecord
class, scripts/grade_lint.py:136, 11 lines

```python
@dataclass
class DecisionRecord
```

HOLE: no docstring

```python
file: str
location: str
decision_id: str | None
tag: GradeTag | None
invalid_wrap: str | None = None
```

reads internal: GradeTag
reads stdlib: builtins.str x4
writes internal: DecisionRecord.decision_id, DecisionRecord.file, DecisionRecord.invalid_wrap, DecisionRecord.location, DecisionRecord.tag

referenced by: 14 sites, this module only
