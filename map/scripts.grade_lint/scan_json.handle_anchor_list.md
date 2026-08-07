# scripts.grade_lint:scan_json.handle_anchor_list
method, scripts/grade_lint.py:431, 23 lines

```python
def handle_anchor_list(entries: list, path_prefix: str) -> None
```

HOLE: no docstring

calls internal: make_violation x2, DecisionRecord, extract_decision_id, find_grade_occurrences, is_placeholder, parse_grade_body, strip_wrapping_backticks
calls stdlib: builtins.enumerate, builtins.isinstance, builtins.len
reads internal: scan_json.file x3, TBD_RE
reads stdlib: builtins.str
unresolved: 4 calls (dispatch-unknown-base)

referenced by: none found
