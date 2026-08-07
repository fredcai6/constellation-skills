# scripts.grade_lint:validate_decision
function, scripts/grade_lint.py:482, 53 lines

```python
def validate_decision(dec: DecisionRecord, known_ids: set[str], ids_provided: bool, mode: str) -> list[Violation]
```

HOLE: no docstring

calls internal: make_violation x8
calls stdlib: builtins.sorted
reads internal: DecisionRecord.file x8, DecisionRecord.location x8, DecisionRecord.invalid_wrap x2, TIERS x2, DecisionRecord.tag, Violation
reads stdlib: builtins.list
unresolved: 10 calls (dispatch-unknown-base), 15 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
