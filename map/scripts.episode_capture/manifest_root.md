# scripts.episode_capture:manifest_root
function, scripts/episode_capture.py:181, 11 lines

```python
def manifest_root(base_dir: Any) -> Path
```

The `agent_work_root` handed to `context_manifest.manifest_path()`.

`manifest_path` composes `<root>/<work-id>/context/<step>.json`, and a run's
checklist lives at `<agent-work>/<work-id>/spine.json` — so the root is the
checklist directory's PARENT, and the manifest lands beside the spine it
describes, inside the same work area. Deliberately not the durable root: the
manifest belongs to one run, and durable resolution is shared across every
linked worktree of a repo, where concurrent runs would collide.

calls stdlib: pathlib.Path x2, os.fspath, os.path.abspath
reads stdlib: os (module) x2, os.path
unresolved: 1 reads (dispatch-unknown-base)

referenced by: 4 sites, this module only
