[map index](../INDEX.md) / [`src.utils.utilization`](INDEX.md)

# `run_jobs`
*function* [s] · [`src/utils/utilization.py:294`](C:/Programs/f1Brainz/src/utils/utilization.py#L294) · 28 lines [s]

**Signature** [s]

```python
def run_jobs(jobs: Sequence, worker_fn: Callable, plan: ResourcePlan, *, on_complete: Optional[Callable] = None, fail_fast: bool = True, logger: Optional[logging.Logger] = None) -> List
```

> Run ``worker_fn`` over ``jobs`` according to ``plan`` and return results in input order.
>
> Args:
>     jobs: a sequence of job payloads (picklable when ``plan.n_workers > 1``).
>     worker_fn: a callable ``(job) -> result`` (picklable when ``plan.n_workers > 1``).
>     plan: the resolved :class:`ResourcePlan`.
>     on_complete: optional ``(completed_count, total, result)`` callback, invoked in
>         the parent process after each job finishes.
>     fail_fast: when True, the first worker error aborts the run and is re-raised
>         wrapped with the failing job's identity (the pool is torn down first).
>     logger: unused override hook reserved for callers that want their own logger;
>         module logging always goes through ``logging.getLogger(__name__)``.
>
> Returns:
>     A list of results in the same order as ``jobs``.

*(everything after the first line above is [s] — the store keeps only the summary line.)*

**Parameters**

- `jobs` — jobs: a sequence of job payloads (picklable when ``plan.n_workers > 1``). [a]
- `worker_fn` — worker_fn: a callable ``(job) -> result`` (picklable when ``plan.n_workers > 1``). [a]
- `plan` — plan: the resolved :class:`ResourcePlan`. [a]
- `on_complete` — on_complete: optional ``(completed_count, total, result)`` callback, invoked in [a]
- `fail_fast` — fail_fast: when True, the first worker error aborts the run and is re-raised [a]
- `logger` — logger: unused override hook reserved for callers that want their own logger; [a]

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `_run_in_pool`, `_run_in_process` |
| reads | internal | `ResourcePlan.n_workers` |

*Not shown: 10 reads of its own parameters.*

**Referenced by**: 4 site(s) across 3 module(s) — src.evo_predictor.gold_cycle.runner_support x2, src.evo_predictor.gold_cycle.runner, src.evo_predictor.sampled_backtest_scoring


---
*Generated from the statement store by `evidence/x11/render_fn.py`. Unmarked facts = `x7b` statements; `[a]` = `x7a`; `[s]` = fetched from source (a logged vocabulary gap). Source-link lines are the store's `q.line` + 1 (defect D1: the store is 0-based and does not say so).*
