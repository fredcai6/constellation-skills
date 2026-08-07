# scripts.apply_episode_delta:_validate_create
function, scripts/apply_episode_delta.py:865, 75 lines

```python
def _validate_create(op: dict) -> None
```

HOLE: no docstring

calls internal: EpisodeDeltaError x14, _reject_newline x2, _validate_assertion_payload x2
calls stdlib: builtins.isinstance x9, builtins.set x4, builtins.sorted x2, builtins.any, builtins.enumerate
reads internal: AGENT_SUPPLIED_KINDS x3, DIAGNOSIS_KINDS x2, MECHANICAL_ALL_FIELDS x2, ASSERTION_ALLOWED_FIELDS, MECHANICAL_INT_FIELDS, MECHANICAL_SCALAR_FIELDS, RUN_RE
reads stdlib: builtins.dict x3, builtins.list x2, builtins.str x2, builtins.bool, builtins.int
unresolved: 10 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
