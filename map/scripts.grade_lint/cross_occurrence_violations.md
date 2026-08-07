# scripts.grade_lint:cross_occurrence_violations
function, scripts/grade_lint.py:537, 27 lines

```python
def cross_occurrence_violations(file: str, decisions: list[DecisionRecord]) -> list[Violation]
```

GL008 (same decision id repeated with the same tier) and GL012 (same

decision id repeated with conflicting tiers), scoped to THIS file only
(ruling: decision:gl012-scoped-per-file). Decisions with no id token are
excluded from this comparison.

calls internal: make_violation x2
calls stdlib: builtins.len x2, builtins.sorted
reads internal: DecisionRecord, Violation
reads stdlib: builtins.list x2, builtins.dict, builtins.str
unresolved: 6 calls (dispatch-unknown-base), 7 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
