# scripts.apply_episode_delta:_new_episode_path
function, scripts/apply_episode_delta.py:746, 5 lines

```python
def _new_episode_path(episode_id: str, root: Path) -> Path
```

Where a brand-new (always-active) episode is written. Not one of section 7's five

named seams (create is g2's own concern, not a retrieval primitive), but it is
exactly as layout-dependent as they are, so it is isolated here the same way.

reads internal: ACTIVE_DIR

referenced by: 1 sites, this module only
