[map index](../INDEX.md) / [`src.utils.utilization`](INDEX.md)

# `_run_in_pool`
*function* [s] · [`src/utils/utilization.py:251`](C:/Programs/f1Brainz/src/utils/utilization.py#L251) · 41 lines [s]

**Signature** [s]

```python
def _run_in_pool(jobs: Sequence, worker_fn: Callable, plan: ResourcePlan, on_complete: Optional[Callable], fail_fast: bool) -> List
```

> Process-pool execution with input-order result reassembly.
>
> Results are placed at their submission index, so the returned list is in input
> order regardless of completion order. ``on_complete`` is invoked in completion
> order. With ``fail_fast`` the first worker error is re-raised wrapped with the
> failing job's identity after the pool is torn down by the ``with`` block.

*(everything after the first line above is [s] — the store keeps only the summary line.)*

**Parameters**

- `jobs` — *[HOLE] undocumented parameter*
- `worker_fn` — *[HOLE] undocumented parameter*
- `plan` — *[HOLE] undocumented parameter*
- `on_complete` — *[HOLE] undocumented parameter*
- `fail_fast` — *[HOLE] undocumented parameter*

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `JobExecutionError`, `_run_in_pool.on_complete`, `_truncated_repr` |
| calls | stdlib | `builtins.enumerate`, `builtins.len`, `concurrent.futures.ProcessPoolExecutor`, `concurrent.futures.as_completed` |
| reads | internal | `ResourcePlan.n_workers`, `ResourcePlan.priority`, `ResourcePlan.threads_per_worker`, `init_worker` |
| reads | stdlib | `builtins.Exception`, `typing.List` |

*Not shown: 20 local-variable reads, 12 local-variable writes; 9 reads of its own parameters.*

**Unresolved by the extractor**: 2 calls (dispatch-unknown-base)

**Referenced by**: 1 site(s) across 1 module(s) (all within this module)


---
*Generated from the statement store by `evidence/x11/render_fn.py`. Unmarked facts = `x7b` statements; `[a]` = `x7a`; `[s]` = fetched from source (a logged vocabulary gap). Source-link lines are the store's `q.line` + 1 (defect D1: the store is 0-based and does not say so).*
