# scripts.grade_lint:scan_block.child_grade_bodies
method, scripts/grade_lint.py:252, 15 lines

```python
def child_grade_bodies(idx: int) -> list[str]
```

Grade bodies on the decision's child line, if any, marking that line

consumed so it is not later mistaken for an orphan grade.

calls internal: find_grade_occurrences
reads internal: scan_block.block_lines x2, LIST_ITEM_RE
unresolved: 3 calls (dispatch-unknown-base)

referenced by: none found
