# scripts.episode_capture:snapshot_path
function, scripts/episode_capture.py:449, 7 lines

```python
def snapshot_path(base_dir: Any, work_id: Any, step: str) -> Path
```

`<agent-work>/<work-id>/mechanical/<step>.json` — beside the step's manifest

(`context/<step>.json`), in the same work area, under a name that says what it
holds. Deliberately not under `episodes/`: this is the mechanical HALF of an
episode, and a directory called `episodes` next to the real store at
`episodes/active/` would invite exactly the wrong reading.

calls internal: manifest_root
calls stdlib: builtins.str, pathlib.Path

referenced by: 1 sites, this module only
