# scripts.run_crew:next_attempt
function, scripts/run_crew.py:153, 11 lines

```python
def next_attempt(entries: list[dict], work_id: str, gate: str, role: str, worktree: str) -> int
```

One past the highest attempt recorded for this gate/role/worktree (>=1).

calls stdlib: builtins.int, builtins.max
unresolved: 5 calls (dispatch-unknown-base)

referenced by: 2 sites, this module only
