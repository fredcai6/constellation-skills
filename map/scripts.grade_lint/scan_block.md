# scripts.grade_lint:scan_block
function, scripts/grade_lint.py:237, 124 lines

```python
def scan_block(file: str, block_lines: list[tuple[int, str]]) -> tuple[list[DecisionRecord], list[Violation]]
```

HOLE: no docstring

- [indent_of](scan_block.indent_of.md) method: HOLE: no docstring
- [child_grade_bodies](scan_block.child_grade_bodies.md) method: Grade bodies on the decision's child line, if any, marking that line
- [detect_wrapped_grade](scan_block.detect_wrapped_grade.md) method: The wrapped-bullet shape: this decision failed to weld (no same-line
- [consume_nested_bullets](scan_block.consume_nested_bullets.md) method: A bullet indented deeper than this decision's own bullet is

calls internal: make_violation x3, find_grade_occurrences x2, DecisionRecord, extract_decision_id, is_placeholder, parse_grade_body, strip_wrapping_backticks
calls stdlib: builtins.len x2, builtins.str x2, builtins.range, builtins.set
reads internal: DecisionRecord, LIST_ITEM_RE, TBD_RE, Violation
reads stdlib: builtins.int x6, builtins.list x3, builtins.str x2, builtins.set
unresolved: 9 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
