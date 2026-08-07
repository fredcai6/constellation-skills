# src.utils.utilization:run_jobs
function, src/utils/utilization.py:294, 28 lines

```python
def run_jobs(jobs: Sequence, worker_fn: Callable, plan: ResourcePlan, *, on_complete: Optional[Callable] = None, fail_fast: bool = True, logger: Optional[logging.Logger] = None) -> List
```

Run ``worker_fn`` over ``jobs`` according to ``plan`` and return results in input order.

Args:
    jobs: a sequence of job payloads (picklable when ``plan.n_workers > 1``).
    worker_fn: a callable ``(job) -> result`` (picklable when ``plan.n_workers > 1``).
    plan: the resolved :class:`ResourcePlan`.
    on_complete: optional ``(completed_count, total, result)`` callback, invoked in
        the parent process after each job finishes.
    fail_fast: when True, the first worker error aborts the run and is re-raised
        wrapped with the failing job's identity (the pool is torn down first).
    logger: unused override hook reserved for callers that want their own logger;
        module logging always goes through ``logging.getLogger(__name__)``.

Returns:
    A list of results in the same order as ``jobs``.

calls internal: _run_in_pool, _run_in_process
reads internal: ResourcePlan.n_workers

referenced by: 4 sites in 3 modules (src.evo_predictor.gold_cycle.runner, src.evo_predictor.gold_cycle.runner_support, src.evo_predictor.sampled_backtest_scoring)
