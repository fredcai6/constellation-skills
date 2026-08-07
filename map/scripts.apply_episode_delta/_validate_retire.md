# scripts.apply_episode_delta:_validate_retire
function, scripts/apply_episode_delta.py:971, 12 lines

```python
def _validate_retire(op: dict) -> None
```

HOLE: no docstring

calls internal: EpisodeDeltaError x2, _reject_newline, _require_str
calls stdlib: builtins.isinstance x2
reads internal: ID_RE
reads stdlib: builtins.str x2
unresolved: 3 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
