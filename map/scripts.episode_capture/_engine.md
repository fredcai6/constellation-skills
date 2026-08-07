# scripts.episode_capture:_engine
function, scripts/episode_capture.py:218, 7 lines

```python
def _engine()
```

The engine module, imported LAZILY for the same reason `context_manifest` is:

`checklist_engine` imports this module, so a top-level import would close the
cycle and break the engine at import time.

reads third-party: checklist_engine (module)

referenced by: 3 sites, this module only
