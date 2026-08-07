[map index](../INDEX.md) / [`src.utils.utilization`](INDEX.md)

# `resolve_resource_plan`
*function* [s] · [`src/utils/utilization.py:108`](C:/Programs/f1Brainz/src/utils/utilization.py#L108) · 67 lines [s]

**Signature** [s]

```python
def resolve_resource_plan(level: str, *, physical_cores: Optional[int] = None, available_mem_gb: Optional[float] = None, mem_per_worker_gb: float = 1.0) -> ResourcePlan
```

> Resolve a utilization ``level`` into a concrete :class:`ResourcePlan`.
>
> Args:
>     level: one of ``UTILIZATION_LEVELS``.
>     physical_cores: physical core count; defaults to detected cores (>= 1).
>     available_mem_gb: available memory in GiB; defaults to detected free memory.
>     mem_per_worker_gb: assumed per-worker memory footprint; gates the RAM cap.
>
> The resolved plan always satisfies ``n_workers * threads_per_worker <= cores``
> and ``n_workers >= 1``. A RAM ceiling may only lower ``n_workers`` (logged when it
> binds). The resolved plan is logged once at info level.
>
> Raises:
>     ValueError: if ``level`` is not a known utilization level.

*(everything after the first line above is [s] — the store keeps only the summary line.)*

**Parameters**

- `level` — level: one of ``UTILIZATION_LEVELS``. [a]
- `physical_cores` — physical_cores: physical core count; defaults to detected cores (>= 1). [a]
- `available_mem_gb` — available_mem_gb: available memory in GiB; defaults to detected free memory. [a]
- `mem_per_worker_gb` — mem_per_worker_gb: assumed per-worker memory footprint; gates the RAM cap. [a]

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `ResourcePlan`, `_apply_ram_cap`, `_detect_available_mem_gb`, `_detect_physical_cores` |
| calls | stdlib | `builtins.max` x2, `builtins.ValueError`, `builtins.int` |
| reads | internal | `_LEVEL_PLANS` x2, `logger` x2, `ResourcePlan.level`, `ResourcePlan.n_workers`, `ResourcePlan.priority`, `ResourcePlan.threads_per_worker`, `UTILIZATION_LEVELS` |

*Not shown: 1 local-variable calls, 22 local-variable reads, 11 local-variable writes; 10 reads of its own parameters.*

**Unresolved by the extractor**: 2 calls (dispatch-unknown-base)

**Referenced by**: 1 site(s) across 1 module(s) — src.evo_predictor.gold_cycle.runner


---
*Generated from the statement store by `evidence/x11/render_fn.py`. Unmarked facts = `x7b` statements; `[a]` = `x7a`; `[s]` = fetched from source (a logged vocabulary gap). Source-link lines are the store's `q.line` + 1 (defect D1: the store is 0-based and does not say so).*
