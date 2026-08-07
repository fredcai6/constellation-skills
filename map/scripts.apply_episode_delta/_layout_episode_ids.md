# scripts.apply_episode_delta:_layout_episode_ids
function, scripts/apply_episode_delta.py:603, 41 lines

```python
def _layout_episode_ids(root: Path, sub: str) -> set[str]
```

Every episode id held by ONE layout directory — the only place a directory

listing becomes a set of ids.

Trap 4. A listing answers "what files are here", never "what episodes are here", and
under a location-based membership rule the gap between those two questions is where
a phantom id comes from. episode_id_for() closes it, and a `*.md` that is NOT a
well-formed episode id is REFUSED rather than skipped: inside active/ or retired/
such a file is either a misfiled record or a placeholder that should not have been
given a `.md` name, and both are things a human must look at. Skipping would be the
silent-omission class again, one directory deeper.

Recursive for the same reason stray_episode_paths() is (trap 6): a record at
`active/old/<id>.md` is a well-formed episode filename at the wrong DEPTH, and a scan
that only lists the top level omits it in silence. Depth is part of the name test
here, so both halves of "is this an episode of this set" are answered in one place.

calls internal: EpisodeDeltaError, episode_id_for
calls stdlib: builtins.set, builtins.sorted
reads internal: ACTIVE_DIR, ID_RE, RETIRED_DIR
reads stdlib: builtins.str x2, builtins.list, builtins.set
unresolved: 7 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: 2 sites, this module only
