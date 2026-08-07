# scripts.apply_episode_delta:validate_delta
function, scripts/apply_episode_delta.py:841, 22 lines

```python
def validate_delta(delta: dict) -> tuple[str, list[dict]]
```

HOLE: no docstring

calls internal: EpisodeDeltaError x3, _validate_amend_assertion, _validate_create, _validate_retire
calls stdlib: builtins.isinstance x2
reads internal: OP_KINDS x2
reads stdlib: builtins.list, builtins.str
unresolved: 3 calls (dispatch-unknown-base)

referenced by: 2 sites, this module only
