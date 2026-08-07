# scripts.recover_crews:detect_conflicts
function, scripts/recover_crews.py:110, 20 lines

```python
def detect_conflicts(entries: list[dict], states: list[str]) -> list[tuple[dict, dict]]
```

Pairs of entries that are BOTH active/resumable for the same

work-id/gate/role/worktree — a two-crews-one-worktree collision. Returns the
later entry paired with the earlier one it conflicts with.

calls stdlib: builtins.zip
reads internal: STATE_ACTIVE, STATE_RESUMABLE
reads stdlib: builtins.dict x4, builtins.tuple x2, builtins.list
unresolved: 5 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
