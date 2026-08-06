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

`src/utils/utilization.py` · 321 lines [s] · 12 top-level, 12 entities total · 11 documented, 1 **holes**

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

- [`ResourcePlan`](#resourceplan) — *class* — An immutable, fully resolved plan for one run.
- [`JobExecutionError`](#jobexecutionerror) — *class* — A worker job failed; carries the failing job's identity for fail-fast surfacing.
- [`_detect_physical_cores`](#-detect-physical-cores) — *function* — Best available physical-core count, never below 1.
- [`_detect_available_mem_gb`](#-detect-available-mem-gb) — *function* — Currently-available system memory in GiB.
- [`_apply_ram_cap`](#-apply-ram-cap) — *function* — Lower ``n_workers`` so the run fits available RAM; never drop below 1.
- [`resolve_resource_plan`](#resolve-resource-plan) — *function* — Resolve a utilization ``level`` into a concrete :class:`ResourcePlan`.
- [`_set_os_priority`](#-set-os-priority) — *function* — Best-effort OS scheduling priority for the current process.
- [`init_worker`](#init-worker) — *function* — Configure the *current* process for a single worker slot.
- [`_truncated_repr`](#-truncated-repr) — *function* — **[HOLE] undocumented**
- [`_run_in_process`](#-run-in-process) — *function* — Sequential, single-process execution. Reproduces the plain sequential path.
- [`_run_in_pool`](#-run-in-pool) — *function* — Process-pool execution with input-order result reassembly.
- [`run_jobs`](#run-jobs) — *function* — Run ``worker_fn`` over ``jobs`` according to ``plan`` and return results in input order.

---

## `ResourcePlan`
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


## `JobExecutionError`
*class* [s] · [`src/utils/utilization.py:68`](C:/Programs/f1Brainz/src/utils/utilization.py#L68) · 2 lines [s]

```python
class JobExecutionError(RuntimeError)
```

> A worker job failed; carries the failing job's identity for fail-fast surfacing.

**Referenced by**: 1 site(s) across 1 module(s) (all within this module)


## `_detect_physical_cores`
*function* [s] · [`src/utils/utilization.py:72`](C:/Programs/f1Brainz/src/utils/utilization.py#L72) · 3 lines [s]

**Signature** [s]

```python
def _detect_physical_cores() -> int
```

> Best available physical-core count, never below 1.

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | stdlib | `os.cpu_count` |
| calls | third-party | `psutil.cpu_count` |
| reads | stdlib | `os (module)` |
| reads | third-party | `psutil (module)` |

**Referenced by**: 1 site(s) across 1 module(s) (all within this module)


## `_detect_available_mem_gb`
*function* [s] · [`src/utils/utilization.py:77`](C:/Programs/f1Brainz/src/utils/utilization.py#L77) · 3 lines [s]

**Signature** [s]

```python
def _detect_available_mem_gb() -> float
```

> Currently-available system memory in GiB.

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | third-party | `psutil.virtual_memory` |
| reads | third-party | `psutil (module)` |

**Unresolved by the extractor**: 1 reads (dispatch-unknown-base)

**Referenced by**: 1 site(s) across 1 module(s) (all within this module)


## `_apply_ram_cap`
*function* [s] · [`src/utils/utilization.py:82`](C:/Programs/f1Brainz/src/utils/utilization.py#L82) · 24 lines [s]

**Signature** [s]

```python
def _apply_ram_cap(n_workers: int, available_mem_gb: float, mem_per_worker_gb: float) -> int
```

> Lower ``n_workers`` so the run fits available RAM; never drop below 1.
>
> Logs one info line *only when the cap actually binds* (i.e. lowers the count),
> naming the before/after worker counts and the memory reason.

*(everything after the first line above is [s] — the store keeps only the summary line.)*

**Parameters**

- `n_workers` — *[HOLE] undocumented parameter*
- `available_mem_gb` — *[HOLE] undocumented parameter*
- `mem_per_worker_gb` — *[HOLE] undocumented parameter*

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | stdlib | `builtins.ValueError`, `builtins.max`, `builtins.min`, `math.floor` |
| reads | internal | `logger` |
| reads | stdlib | `math (module)` |

*Not shown: 4 local-variable reads, 2 local-variable writes; 9 reads of its own parameters.*

**Unresolved by the extractor**: 1 calls (dispatch-unknown-base)

**Referenced by**: 1 site(s) across 1 module(s) (all within this module)


## `resolve_resource_plan`
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


## `_set_os_priority`
*function* [s] · [`src/utils/utilization.py:177`](C:/Programs/f1Brainz/src/utils/utilization.py#L177) · 24 lines [s]

**Signature** [s]

```python
def _set_os_priority(priority: str) -> None
```

> Best-effort OS scheduling priority for the current process.
>
> Windows uses psutil priority classes; POSIX uses ``os.nice``. "normal" leaves the
> process untouched. Any failure is swallowed (priority is an optimization, not a
> correctness requirement).

*(everything after the first line above is [s] — the store keeps only the summary line.)*

**Parameters**

- `priority` — *[HOLE] undocumented parameter*

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | stdlib | `os.nice` |
| calls | third-party | `psutil.Process` |
| reads | internal | `logger` |
| reads | stdlib | `os (module)` x2, `builtins.Exception`, `os.name` |
| reads | third-party | `psutil (module)` x3 |

*Not shown: 5 local-variable reads, 4 local-variable writes; 4 reads of its own parameters.*

**Unresolved by the extractor**: 4 calls (dispatch-unknown-base), 2 calls (dynamic)

**Referenced by**: 1 site(s) across 1 module(s) (all within this module)


## `init_worker`
*function* [s] · [`src/utils/utilization.py:203`](C:/Programs/f1Brainz/src/utils/utilization.py#L203) · 21 lines [s]

**Signature** [s]

```python
def init_worker(threads_per_worker: int, priority: str) -> None
```

> Configure the *current* process for a single worker slot.
>
> Module-level and side-effect-only so it is usable as a ``ProcessPoolExecutor``
> initializer (which must be importable/picklable). Sets the BLAS/OMP thread-cap
> environment variables, then — if torch is importable — caps torch's thread pool,
> then applies a best-effort OS priority. The torch import is guarded so the module
> and this function work even when torch is absent.

*(everything after the first line above is [s] — the store keeps only the summary line.)*

**Parameters**

- `threads_per_worker` — *[HOLE] undocumented parameter*
- `priority` — *[HOLE] undocumented parameter*

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `_set_os_priority` |
| calls | stdlib | `builtins.str` |
| reads | internal | `logger` |
| reads | stdlib | `builtins.Exception`, `os (module)`, `os.environ` |
| writes | stdlib | `os.environ[]` |

*Not shown: 3 local-variable reads, 2 local-variable writes; 3 reads of its own parameters.*

**Unresolved by the extractor**: 2 calls (dispatch-unknown-base)

**Referenced by**: 2 site(s) across 1 module(s) (all within this module)


## `_truncated_repr`
*function* [s] · [`src/utils/utilization.py:226`](C:/Programs/f1Brainz/src/utils/utilization.py#L226) · 5 lines [s]

**Signature** [s]

```python
def _truncated_repr(job: object) -> str
```

> **[HOLE] no docstring** — this entity's purpose is not recorded in the source. Nothing in the store can supply it.

**Parameters**

- `job` — *[HOLE] undocumented parameter*

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | stdlib | `builtins.len`, `builtins.repr` |
| reads | internal | `_JOB_REPR_LIMIT` x2 |

*Not shown: 3 local-variable reads, 1 local-variable writes; 1 reads of its own parameters.*

**Referenced by**: 1 site(s) across 1 module(s) (all within this module)


## `_run_in_process`
*function* [s] · [`src/utils/utilization.py:233`](C:/Programs/f1Brainz/src/utils/utilization.py#L233) · 16 lines [s]

**Signature** [s]

```python
def _run_in_process(jobs: Sequence, worker_fn: Callable, plan: ResourcePlan, on_complete: Optional[Callable]) -> List
```

> Sequential, single-process execution. Reproduces the plain sequential path.

**Parameters**

- `jobs` — *[HOLE] undocumented parameter*
- `worker_fn` — *[HOLE] undocumented parameter*
- `plan` — *[HOLE] undocumented parameter*
- `on_complete` — *[HOLE] undocumented parameter*

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `_run_in_process.on_complete`, `_run_in_process.worker_fn`, `init_worker` |
| calls | stdlib | `builtins.enumerate`, `builtins.len` |
| reads | internal | `ResourcePlan.priority`, `ResourcePlan.threads_per_worker` |
| reads | stdlib | `typing.List` |

*Not shown: 7 local-variable reads, 5 local-variable writes; 5 reads of its own parameters.*

**Unresolved by the extractor**: 1 calls (dispatch-unknown-base)

**Referenced by**: 1 site(s) across 1 module(s) (all within this module)


## `_run_in_pool`
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


## `run_jobs`
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

**Provenance**: unmarked facts come from `evidence/x7b/statements.jsonl`; `[a]` from `evidence/x7a/statements.jsonl`; `[s]` had to be fetched from source by `evidence/x11/supplement.py` and is a logged statement-vocabulary gap. No sentence on this page was written by a model.

Line numbers in source links are the store's `q.line` **+ 1**: x7b records 0-based lines for all 87 entities and the schema does not say so (defect D1).
