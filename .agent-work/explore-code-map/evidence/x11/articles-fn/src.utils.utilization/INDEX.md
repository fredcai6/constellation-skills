[map index](../INDEX.md)

# `src.utils.utilization`

> Shared, F1-agnostic resource-utilization policy core.
>
> This module decides *how hard the machine is pushed* without ever changing *what is
> computed*. It maps a coarse utilization level to a concrete worker/thread/priority
> plan and runs a list of jobs through that plan — either in a process pool or, at one
> worker, in a plain in-process loop.
>
> Determinism contract (load-bearing for every caller):
>   * `run_jobs` always returns results in **input order**, byte-identical regardless of
>     `n_workers`, because results are reassembled by their submission index.
>   * `n_workers == 1` short-circuits to a sequential in-process loop — no pool, no
>     pickling — so it reproduces the plain sequential path exactly.
>
> The module is intentionally free of any F1/domain concepts (no DB, calendar, or evo
> imports) and holds no mutable module-level state. It must import cleanly even when
> `torch` is not installed; the torch import lives inside `init_worker` and is guarded.

*(everything after the first line above is [s].)*

`src/utils/utilization.py` · 321 lines [s] · 12 entities · 11 documented, 1 **holes**

## Dependencies

**Imports (stdlib)**: `__future__.annotations`, `concurrent.futures.ProcessPoolExecutor`, `concurrent.futures.as_completed`, `dataclasses.dataclass`, `logging`, `math`, `os`, `typing.Callable`, `typing.List`, `typing.Optional`, `typing.Sequence`
**Imports (third-party)**: `psutil`, `torch`

**Imported by** (5 modules in the extraction window): `src.evo_predictor.gold_cycle.config`, `src.evo_predictor.gold_cycle.runner`, `src.evo_predictor.gold_cycle.runner_support`, `src.evo_predictor.sampled_backtest`, `src.evo_predictor.sampled_backtest_scoring`

## Module-level constants

| name | annotation [s] | value [s] | line | in store? |
| --- | --- | --- | --- | --- |
| `logger` | — | `logging.getLogger(__name__)` | 30 | name only |
| `UTILIZATION_LEVELS` | — | `('background', 'balanced', 'max')` | 34 | name only |
| `_PRIORITIES` | — | `('idle', 'below_normal', 'normal')` | 37 | name only |
| `_LEVEL_PLANS` | — | `{'background': (lambda cores: 1, 1, 'below_normal'), 'balanced': (l...` | 41 | name only |
| `_JOB_REPR_LIMIT` | — | `120` | 48 | name only |

## Contents

- [`ResourcePlan`](ResourcePlan.md) — *class* [s] — An immutable, fully resolved plan for one run.
- [`JobExecutionError`](JobExecutionError.md) — *class* [s] — A worker job failed; carries the failing job's identity for fail-fast surfacing.
- [`_detect_physical_cores`](_detect_physical_cores.md) — *function* [s] — Best available physical-core count, never below 1.
- [`_detect_available_mem_gb`](_detect_available_mem_gb.md) — *function* [s] — Currently-available system memory in GiB.
- [`_apply_ram_cap`](_apply_ram_cap.md) — *function* [s] — Lower ``n_workers`` so the run fits available RAM; never drop below 1.
- [`resolve_resource_plan`](resolve_resource_plan.md) — *function* [s] — Resolve a utilization ``level`` into a concrete :class:`ResourcePlan`.
- [`_set_os_priority`](_set_os_priority.md) — *function* [s] — Best-effort OS scheduling priority for the current process.
- [`init_worker`](init_worker.md) — *function* [s] — Configure the *current* process for a single worker slot.
- [`_truncated_repr`](_truncated_repr.md) — *function* [s] — **[HOLE] undocumented**
- [`_run_in_process`](_run_in_process.md) — *function* [s] — Sequential, single-process execution. Reproduces the plain sequential path.
- [`_run_in_pool`](_run_in_pool.md) — *function* [s] — Process-pool execution with input-order result reassembly.
- [`run_jobs`](run_jobs.md) — *function* [s] — Run ``worker_fn`` over ``jobs`` according to ``plan`` and return results in input order.
---
*Generated from the statement store by `evidence/x11/render_fn.py`. Unmarked facts = `x7b` statements; `[a]` = `x7a`; `[s]` = fetched from source (a logged vocabulary gap). Source-link lines are the store's `q.line` + 1 (defect D1: the store is 0-based and does not say so).*
