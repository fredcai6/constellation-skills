# scripts.recover_crews:classify_registry
function, scripts/recover_crews.py:166, 14 lines

```python
def classify_registry(entries: list[dict], *, alive: AlivePredicate, result_present: ResultPredicate) -> list[tuple[dict, str]]
```

Classify every entry, upgrading members of a same-target collision to

`conflict` so Commander stops rather than blindly resuming/launching.

calls internal: classify_entry, detect_conflicts
calls stdlib: builtins.enumerate, builtins.list, builtins.zip
reads internal: STATE_CONFLICT

referenced by: 1 sites, this module only
