# scripts.checklist_engine:_gauge_path
function, scripts/checklist_engine.py:1190, 9 lines

```python
def _gauge_path(base_dir: Path | None) -> Path | None
```

The gauge file for this checklist: `.agent-work/<work_id>/gauge.json`, a

SIBLING of the spine — #180's writer drops it at `Path(spine).parent /
"gauge.json"`, and `base_dir` IS that spine directory. Returns None when the
location is unresolvable (no `base_dir`, e.g. a checklist processed without a
file path): an unresolvable work_id yields no reading and no advice.

calls stdlib: pathlib.Path

referenced by: 3 sites, this module only
