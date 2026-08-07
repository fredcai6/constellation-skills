# scripts.apply_episode_delta:_next_episode_id
function, scripts/apply_episode_delta.py:822, 13 lines

```python
def _next_episode_id(run: str, known_ids: set[str]) -> str
```

Zero-agent-effort id assignment: scan existing <run>-*.md basenames (across

every episode for that run regardless of retirement status — a retired episode's
sequence number is still taken) for the current max and increment. No counter
file, no UUID.

calls stdlib: builtins.int, builtins.len, builtins.max
unresolved: 2 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
