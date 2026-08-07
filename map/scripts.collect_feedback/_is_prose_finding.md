# scripts.collect_feedback:_is_prose_finding
function, scripts/collect_feedback.py:178, 5 lines

```python
def _is_prose_finding(entry: dict[str, str]) -> bool
```

Prose blocks always have a candidate (derived from the heading), so a

prose entry is a real finding only if it also carries observed or proposal.

calls stdlib: builtins.any
unresolved: 2 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
