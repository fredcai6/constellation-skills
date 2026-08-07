# scripts.checklist_engine:journal_path
function, scripts/checklist_engine.py:2610, 5 lines

```python
def journal_path(spine_path: Path) -> Path
```

The journal sidecar for a spine file: ``<spine>.journal`` (so

``spine.json`` -> ``spine.json.journal``, and a child ``review.json`` gets its
own ``review.json.journal``).

calls stdlib: builtins.str, pathlib.Path

referenced by: 1 sites, this module only
