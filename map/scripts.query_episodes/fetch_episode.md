# scripts.query_episodes:fetch_episode
function, scripts/query_episodes.py:154, 10 lines

```python
def fetch_episode(episode_id: str, root: Path)
```

Fetch one episode by id. Returns the parsed Episode, or None if no episode with

that id exists. Resolves its path through resolve_episode_path() (section 7) and
reads whatever that returns — it never constructs a path itself, because which
directory (if any) holds the file IS the open layout question. No scan, no
membership check (section 8).

calls internal: _read_episode, writer
unresolved: 1 calls (dispatch-unknown-base)

referenced by: 3 sites, this module only
