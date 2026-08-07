# src.utils.utilization:_run_in_pool
function, src/utils/utilization.py:251, 41 lines

```python
def _run_in_pool(jobs: Sequence, worker_fn: Callable, plan: ResourcePlan, on_complete: Optional[Callable], fail_fast: bool) -> List
```

Process-pool execution with input-order result reassembly.

Results are placed at their submission index, so the returned list is in input
order regardless of completion order. ``on_complete`` is invoked in completion
order. With ``fail_fast`` the first worker error is re-raised wrapped with the
failing job's identity after the pool is torn down by the ``with`` block.

calls internal: JobExecutionError, _run_in_pool.on_complete, _truncated_repr
calls stdlib: builtins.enumerate, builtins.len, concurrent.futures.ProcessPoolExecutor, concurrent.futures.as_completed
reads internal: ResourcePlan.n_workers, ResourcePlan.priority, ResourcePlan.threads_per_worker, init_worker
reads stdlib: builtins.Exception, typing.List
unresolved: 2 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
