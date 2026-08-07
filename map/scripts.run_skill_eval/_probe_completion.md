# scripts.run_skill_eval:_probe_completion
function, scripts/run_skill_eval.py:928, 9 lines

```python
def _probe_completion(run_dir: Path, since: float) -> tuple[bool, bool]
```

Whether the run's completion artifact is present and FRESH (mtime at/after

`since`, floored to whole seconds so coarse fs mtime cannot falsely flag a
same-second write — the run_crew freshness convention).

calls stdlib: builtins.float, builtins.int
reads internal: COMPLETION_ARTIFACT
unresolved: 2 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
