# scripts.grade_lint:scan_block.detect_wrapped_grade
method, scripts/grade_lint.py:268, 25 lines

```python
def detect_wrapped_grade(idx: int) -> int | None
```

The wrapped-bullet shape: this decision failed to weld (no same-line

or next-non-blank tag), because its own text runs onto one or more
CONTINUATION lines first -- non-blank, not a list item, not itself
carrying '@grade:' -- before a line that finally carries the tag. The
weld rule itself stays exactly same-line-or-next-non-blank (do not
extend it: that would erode the locality guarantee); this is a
diagnostic-only lookahead that renames the failure, it never makes the
tag count. Stops at the first blank line or list-item line -- either
means the decision's own paragraph is over, so any grade beyond it
belongs to something else, not this decision -- and returns None
(not a wrap) in that case, or if the block ends first.

calls internal: find_grade_occurrences
reads internal: LIST_ITEM_RE, scan_block.block_lines
unresolved: 2 calls (dispatch-unknown-base)

referenced by: none found
