# scripts.apply_episode_delta:_validate_amend_assertion
function, scripts/apply_episode_delta.py:958, 11 lines

```python
def _validate_amend_assertion(op: dict) -> None
```

HOLE: no docstring

calls internal: EpisodeDeltaError x3, _require_str
calls stdlib: builtins.isinstance x2, re.fullmatch
reads internal: LIFECYCLE_STANDINGS x2, ID_RE
reads stdlib: builtins.str x2, re (module)
unresolved: 4 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
