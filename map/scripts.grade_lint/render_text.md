# scripts.grade_lint:render_text
function, scripts/grade_lint.py:685, 10 lines

```python
def render_text(violations: list[Violation], ledger: dict, quiet: bool) -> None
```

HOLE: no docstring

calls internal: ledger_summary_line x2
calls stdlib: builtins.print x5, builtins.len
unresolved: 6 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
