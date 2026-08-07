[map index](../INDEX.md) / [`src.utils.utilization`](INDEX.md)

# `_run_in_process`
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


---
*Generated from the statement store by `evidence/x11/render_fn.py`. Unmarked facts = `x7b` statements; `[a]` = `x7a`; `[s]` = fetched from source (a logged vocabulary gap). Source-link lines are the store's `q.line` + 1 (defect D1: the store is 0-based and does not say so).*
