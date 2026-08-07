# src.utils.utilization:resolve_resource_plan
function, src/utils/utilization.py:108, 67 lines

```python
def resolve_resource_plan(level: str, *, physical_cores: Optional[int] = None, available_mem_gb: Optional[float] = None, mem_per_worker_gb: float = 1.0) -> ResourcePlan
```

Resolve a utilization ``level`` into a concrete :class:`ResourcePlan`.

Args:
    level: one of ``UTILIZATION_LEVELS``.
    physical_cores: physical core count; defaults to detected cores (>= 1).
    available_mem_gb: available memory in GiB; defaults to detected free memory.
    mem_per_worker_gb: assumed per-worker memory footprint; gates the RAM cap.

The resolved plan always satisfies ``n_workers * threads_per_worker <= cores``
and ``n_workers >= 1``. A RAM ceiling may only lower ``n_workers`` (logged when it
binds). The resolved plan is logged once at info level.

Raises:
    ValueError: if ``level`` is not a known utilization level.

calls internal: ResourcePlan, _apply_ram_cap, _detect_available_mem_gb, _detect_physical_cores
calls stdlib: builtins.max x2, builtins.ValueError, builtins.int
reads internal: _LEVEL_PLANS x2, logger x2, ResourcePlan.level, ResourcePlan.n_workers, ResourcePlan.priority, ResourcePlan.threads_per_worker, UTILIZATION_LEVELS
unresolved: 2 calls (dispatch-unknown-base)

referenced by: 1 sites in 1 modules (src.evo_predictor.gold_cycle.runner)
