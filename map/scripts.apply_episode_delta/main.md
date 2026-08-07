# scripts.apply_episode_delta:main
function, scripts/apply_episode_delta.py:1247, 37 lines

```python
def main(argv: list[str] | None = None) -> int
```

HOLE: no docstring

calls internal: _dry_run_log, apply_delta, store_root
calls stdlib: builtins.print x4, argparse.ArgumentParser, json.loads
reads internal: EpisodeDeltaError
reads stdlib: sys (module) x3, sys.stderr x3, builtins.OSError x2, json (module) x2, pathlib.Path x2, argparse (module), builtins.__doc__, json.JSONDecodeError
unresolved: 5 calls (dispatch-unknown-base), 4 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
