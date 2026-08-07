# src.utils.utilization:_apply_ram_cap
function, src/utils/utilization.py:82, 24 lines

```python
def _apply_ram_cap(n_workers: int, available_mem_gb: float, mem_per_worker_gb: float) -> int
```

Lower ``n_workers`` so the run fits available RAM; never drop below 1.

Logs one info line *only when the cap actually binds* (i.e. lowers the count),
naming the before/after worker counts and the memory reason.

calls stdlib: builtins.ValueError, builtins.max, builtins.min, math.floor
reads internal: logger
reads stdlib: math (module)
unresolved: 1 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
