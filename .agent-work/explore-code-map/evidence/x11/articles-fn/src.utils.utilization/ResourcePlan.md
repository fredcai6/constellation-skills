# src.utils.utilization:ResourcePlan
class, src/utils/utilization.py:52, 14 lines

```python
@dataclass(frozen=True)
class ResourcePlan
```

An immutable, fully resolved plan for one run.

Attributes:
    level: the requested utilization level (one of ``UTILIZATION_LEVELS``).
    n_workers: number of worker processes (>= 1).
    threads_per_worker: intra-worker thread cap (>= 1).
    priority: OS scheduling priority label (one of ``_PRIORITIES``).

```python
level: str
n_workers: int
threads_per_worker: int
priority: str
```

reads stdlib: builtins.int x2, builtins.str x2
writes internal: ResourcePlan.level, ResourcePlan.n_workers, ResourcePlan.priority, ResourcePlan.threads_per_worker

referenced by: 12 sites in 5 modules (src.evo_predictor.gold_cycle.runner, src.evo_predictor.gold_cycle.runner_support, src.evo_predictor.sampled_backtest, src.evo_predictor.sampled_backtest_scoring)
