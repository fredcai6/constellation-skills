# scripts.apply_episode_delta:apply_retirement
function, scripts/apply_episode_delta.py:769, 30 lines

```python
def apply_retirement(episode: Episode, reason: str, *, retired_at: str = '', consolidated_into: str = '', superseded_by: str = '') -> None
```

THE retirement write-side seam (section 7): the entire CONTENT effect of a retire

op. The writer must call this and never inline a field-only write or a file-move at
the call site — the layout effect (the file moves into the archive) is expressed
separately, in the write plan built by _Transaction.write_plan(), which asks
destination_for() (below) for the destination.

This function only ever mutates the in-memory Episode; it performs no I/O itself, so
the all-or-nothing guarantee (C4) never depends on ordering retirements before other
ops — and, since the field update and the move are two halves of ONE write plan
entry, no plan this writer builds can disagree with itself: "fields updated but file
not moved" (or the reverse) has no representation in it.

That is a claim about the PLAN, and it is as far as the claim goes. It does not say
the store can never be half-retired: a hard kill between the placement of the archived
copy and the removal of the source runs no compensation at all, which is why
_reject_half_retired() exists and why every read seam and the writer's own pre-flight
check for that residue rather than assuming it away.

writes internal: Episode.consolidated_into, Episode.retired_at, Episode.retired_reason, Episode.status, Episode.superseded_by

referenced by: 1 sites, this module only
