# scripts.apply_episode_delta:destination_for
function, scripts/apply_episode_delta.py:801, 16 lines

```python
def destination_for(episode: Episode, root: Path, current_path: Path) -> Path
```

The layout-dependent HALF of retiring, bound to Option A: where should this

episode's file live NOW, given its current state and where it currently is?

The whole routing decision lives here, including the test on the episode's own
status, so no caller anywhere reads that field to decide a path. That containment is
the point: a caller that branched on `status` itself and then picked a directory
would be an inlined layout check wearing a delegation's clothes, and it is exactly
what §7's seam table exists to prevent.

Isolated from apply_retirement()'s field diff so the two stay independently testable,
and so the move is expressed once — the write plan then carries it, which is what
makes the field update and the move land or fail together (see _Transaction.commit).

reads internal: Episode.episode_id, Episode.status, RETIRED_DIR

referenced by: 1 sites, this module only
