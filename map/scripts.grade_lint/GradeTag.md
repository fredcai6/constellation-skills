# scripts.grade_lint:GradeTag
class, scripts/grade_lint.py:126, 7 lines

```python
@dataclass
class GradeTag
```

HOLE: no docstring

```python
tier: str | None
provenance: str | None
leans: list[str] = field(default_factory=list)
settle: str | None = None
malformed_segments: list[str] = field(default_factory=list)
raw: str = ''
```

calls stdlib: dataclasses.field x2
reads stdlib: builtins.str x6, builtins.list x4
writes internal: GradeTag.leans, GradeTag.malformed_segments, GradeTag.provenance, GradeTag.raw, GradeTag.settle, GradeTag.tier

referenced by: 3 sites, this module only
