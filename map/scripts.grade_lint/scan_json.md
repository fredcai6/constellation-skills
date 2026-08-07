# scripts.grade_lint:scan_json
function, scripts/grade_lint.py:427, 48 lines

```python
def scan_json(file: str, data) -> tuple[list[DecisionRecord], list[Violation]]
```

HOLE: no docstring

- [handle_anchor_list](scan_json.handle_anchor_list.md) method: HOLE: no docstring

calls stdlib: builtins.isinstance x7
reads internal: DecisionRecord, Violation
reads stdlib: builtins.dict x5, builtins.list x5, builtins.str
unresolved: 6 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
