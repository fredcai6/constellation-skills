[map index](../INDEX.md) / [`src.utils.utilization`](INDEX.md)

# `_apply_ram_cap`
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


---
*Generated from the statement store by `evidence/x11/render_fn.py`. Unmarked facts = `x7b` statements; `[a]` = `x7a`; `[s]` = fetched from source (a logged vocabulary gap). Source-link lines are the store's `q.line` + 1 (defect D1: the store is 0-based and does not say so).*
