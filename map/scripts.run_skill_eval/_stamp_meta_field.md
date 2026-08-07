# scripts.run_skill_eval:_stamp_meta_field
function, scripts/run_skill_eval.py:633, 15 lines

```python
def _stamp_meta_field(run_dir, **fields) -> None
```

Best-effort merge of `fields` into a run's launch meta.json (only while it is

still `launched`). Used to record the subject PID at spawn so an external reaper
can tree-kill an orphaned subject after a runner death. Never raises.

calls stdlib: json.dumps, json.loads, pathlib.Path
reads stdlib: json (module) x2, builtins.OSError, builtins.ValueError
unresolved: 5 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
