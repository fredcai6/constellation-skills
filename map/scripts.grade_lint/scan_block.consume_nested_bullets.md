# scripts.grade_lint:scan_block.consume_nested_bullets
method, scripts/grade_lint.py:294, 15 lines

```python
def consume_nested_bullets(idx: int) -> None
```

A bullet indented deeper than this decision's own bullet is

elaboration ON the decision, not a second decision. Without this, a
clarifying sub-bullet under a properly graded decision reports as an
ungraded decision — a false FAIL on a valid plan.

calls stdlib: builtins.range
reads internal: scan_block.block_lines x2, LIST_ITEM_RE
unresolved: 3 calls (dispatch-unknown-base)

referenced by: none found
