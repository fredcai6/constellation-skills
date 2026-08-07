# scripts.file_issue_set:build_epic_body
function, scripts/file_issue_set.py:99, 13 lines

```python
def build_epic_body(manifest: dict, ekey: str) -> str
```

The downstream seam: wave-ordered task list + AFK/HITL labels + the

idempotency marker.

calls internal: key_marker, wave_order
calls stdlib: builtins.enumerate
unresolved: 10 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
