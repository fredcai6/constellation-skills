# scripts.apply_episode_delta:iter_episode_ids
function, scripts/apply_episode_delta.py:669, 33 lines

```python
def iter_episode_ids(root: Path, include_retired: bool) -> list[str]
```

Base enumeration seam (section 7), bound to Option A.

Ordinary enumeration is the ordinary set and nothing else — the archive is not a
second live search space that this function has to remember to exclude, which is
exactly the ruling's second half. `include_retired=True` is the deliberate
history-inclusive act: it UNIONS both directories. Trap 2 is forgetting that union
and returning only the active half, so the union is written once, here, and no caller
repeats it.

Two malformed-store conditions raise here rather than being answered around, because
both would otherwise produce a silently wrong candidate set — and because putting
them in the seam every reader AND the writer's own id-assignment scan already goes
through means no caller has to remember them:

  * a stray at the flat root (trap 3) — it belongs to neither set, so every
    enumeration omits it, and the writer would happily mint an id the stray holds;
  * an id in both directories — an interrupted retirement (see _reject_half_retired).

The archive is listed even for an ordinary scan, solely to check the second
condition. That listing can only ever produce a REFUSAL; it never contributes a
candidate, so the archive remains an archive rather than a second search space.

Both directory listings go through _layout_episode_ids(), so a file that is not an
episode never becomes a candidate id here — the classifier is applied where the
membership rule is applied, which is the coupling whose absence bricked this store
the first time round.

calls internal: _layout_episode_ids x2, _reject_half_retired, _reject_strays, _require_store_layout
calls stdlib: builtins.sorted
reads internal: ACTIVE_DIR, RETIRED_DIR

referenced by: 1 sites, this module only
