# scripts.query_episodes:main
function, scripts/query_episodes.py:475, 98 lines

```python
def main(argv: list[str] | None = None) -> int
```

HOLE: no docstring

- [add_archive_flag](main.add_archive_flag.md) method: HOLE: no docstring

calls internal: _envelope, enumerate_episodes, fetch_episode, neighbours, select_episodes, store_root, writer
calls stdlib: builtins.print x5, argparse.ArgumentParser, json.dumps
reads internal: EpisodeNotFound, QueryError
reads stdlib: sys (module) x4, sys.stderr x4, argparse (module), json (module), pathlib.Path
unresolved: 11 calls (dispatch-unknown-base), 1 calls (dynamic), 12 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
