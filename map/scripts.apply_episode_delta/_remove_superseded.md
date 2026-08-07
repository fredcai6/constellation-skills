# scripts.apply_episode_delta:_remove_superseded
function, scripts/apply_episode_delta.py:999, 7 lines

```python
def _remove_superseded(path: Path) -> None
```

Remove the source path a moved episode has left behind — the second half of a

retirement's move, and the only place in the module that deletes a live episode file.

Named for the same reason as _place(): this is the exact step whose failure would
leave an id in BOTH active/ and retired/, so a test has to be able to force it.

unresolved: 1 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
