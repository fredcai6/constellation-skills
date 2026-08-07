# tests.test_run_skill_eval:_seed_run_dir
function, tests/test_run_skill_eval.py:932, 10 lines

```python
def _seed_run_dir(temp_root: Path, index: int, *, meta: dict, artifact: bool) -> Path
```

Seed a run-<index>/ with a meta.json and (optionally) a passing workspace,

modelling the on-disk state a prior invocation left behind.

calls stdlib: json.dumps
reads internal: rse
reads stdlib: json (module)
unresolved: 3 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: 7 sites, this module only
