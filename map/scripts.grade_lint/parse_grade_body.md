# scripts.grade_lint:parse_grade_body
function, scripts/grade_lint.py:186, 28 lines

```python
def parse_grade_body(body: str) -> GradeTag
```

HOLE: no docstring

calls internal: GradeTag
calls stdlib: builtins.len x2, re.match x2
reads internal: MIDDOT
reads stdlib: re (module) x4, builtins.str x3, builtins.list x2, re.IGNORECASE x2
unresolved: 13 calls (dispatch-unknown-base)

referenced by: 2 sites, this module only
