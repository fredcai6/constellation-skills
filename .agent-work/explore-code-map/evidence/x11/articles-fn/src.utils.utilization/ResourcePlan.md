[map index](../INDEX.md) / [`src.utils.utilization`](INDEX.md)

# `ResourcePlan`
*class* [s] · [`src/utils/utilization.py:52`](C:/Programs/f1Brainz/src/utils/utilization.py#L52) · 14 lines [s]

```python
class ResourcePlan
```
**Decorators** [s]: `@dataclass(frozen=True)`

> An immutable, fully resolved plan for one run.
>
> Attributes:
>     level: the requested utilization level (one of ``UTILIZATION_LEVELS``).
>     n_workers: number of worker processes (>= 1).
>     threads_per_worker: intra-worker thread cap (>= 1).
>     priority: OS scheduling priority label (one of ``_PRIORITIES``).

*(everything after the first line above is [s] — the store keeps only the summary line.)*

**Fields**

| name | annotation [s] | value [s] | line | in store? |
| --- | --- | --- | --- | --- |
| `level` | `str` | — | 62 | name only |
| `n_workers` | `int` | — | 63 | name only |
| `threads_per_worker` | `int` | — | 64 | name only |
| `priority` | `str` | — | 65 | name only |

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| reads | stdlib | `builtins.int` x2, `builtins.str` x2 |
| writes | internal | `ResourcePlan.level`, `ResourcePlan.n_workers`, `ResourcePlan.priority`, `ResourcePlan.threads_per_worker` |

**Referenced by**: 12 site(s) across 5 module(s) — src.evo_predictor.gold_cycle.runner x3, src.evo_predictor.gold_cycle.runner_support x2, src.evo_predictor.sampled_backtest, src.evo_predictor.sampled_backtest_scoring


---
*Generated from the statement store by `evidence/x11/render_fn.py`. Unmarked facts = `x7b` statements; `[a]` = `x7a`; `[s]` = fetched from source (a logged vocabulary gap). Source-link lines are the store's `q.line` + 1 (defect D1: the store is 0-based and does not say so).*
