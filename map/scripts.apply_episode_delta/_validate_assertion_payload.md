# scripts.apply_episode_delta:_validate_assertion_payload
function, scripts/apply_episode_delta.py:942, 14 lines

```python
def _validate_assertion_payload(payload: dict, where: str) -> None
```

HOLE: no docstring

calls internal: EpisodeDeltaError x3, _require_str
calls stdlib: builtins.set x2, builtins.isinstance, builtins.sorted
reads internal: ASSERTION_ALLOWED_FIELDS x2, STRENGTHS x2
reads stdlib: builtins.dict
unresolved: 1 calls (dispatch-unknown-base)

referenced by: 2 sites, this module only
