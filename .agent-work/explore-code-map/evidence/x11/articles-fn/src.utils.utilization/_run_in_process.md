# src.utils.utilization:_run_in_process
function, src/utils/utilization.py:233, 16 lines

```python
def _run_in_process(jobs: Sequence, worker_fn: Callable, plan: ResourcePlan, on_complete: Optional[Callable]) -> List
```

Sequential, single-process execution. Reproduces the plain sequential path.

calls internal: _run_in_process.on_complete, _run_in_process.worker_fn, init_worker
calls stdlib: builtins.enumerate, builtins.len
reads internal: ResourcePlan.priority, ResourcePlan.threads_per_worker
reads stdlib: typing.List
unresolved: 1 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
