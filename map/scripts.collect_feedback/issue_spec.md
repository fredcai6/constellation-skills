# scripts.collect_feedback:issue_spec
function, scripts/collect_feedback.py:364, 40 lines

```python
def issue_spec(fp: str, hits: list[tuple[str, dict[str, str]]], labels=()) -> dict
```

Render one finding group into a fileable GitHub issue spec.

calls stdlib: builtins.len x6, builtins.list, builtins.sorted
unresolved: 9 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
