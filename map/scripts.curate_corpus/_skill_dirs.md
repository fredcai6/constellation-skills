# scripts.curate_corpus:_skill_dirs
function, scripts/curate_corpus.py:347, 7 lines

```python
def _skill_dirs(root: Path) -> list[Path]
```

Immediate subdirectories that are candidate skills. Dirs whose name starts

with '_' or '.' (e.g. `_shared`) are infrastructure, not skills, and skipped.

calls stdlib: builtins.sorted
unresolved: 4 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
