# scripts.run_skill_eval:is_infra_marker
function, scripts/run_skill_eval.py:321, 5 lines

```python
def is_infra_marker(text) -> bool
```

Whether `text` carries a transient-environment marker (usage/rate limit,

quota, overloaded, 429). PURE. A hit fences the run as inconclusive.

calls stdlib: builtins.any
reads internal: INFRA_MARKERS
unresolved: 1 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
