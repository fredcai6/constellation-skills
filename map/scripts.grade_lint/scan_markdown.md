# scripts.grade_lint:scan_markdown
function, scripts/grade_lint.py:363, 41 lines

```python
def scan_markdown(file: str, text: str) -> tuple[list[DecisionRecord], list[Violation]]
```

HOLE: no docstring

- [flush_block](scan_markdown.flush_block.md) method: HOLE: no docstring

calls stdlib: builtins.enumerate, builtins.len
reads internal: DecisionRecord, FENCE_RE, HEADING_RE, RECOGNIZED_RE, Violation
reads stdlib: builtins.list x3, builtins.int x2, builtins.str, builtins.tuple
unresolved: 7 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
