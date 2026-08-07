[map index](../INDEX.md) / [`src.utils.utilization`](INDEX.md)

# `init_worker`
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


---
*Generated from the statement store by `evidence/x11/render_fn.py`. Unmarked facts = `x7b` statements; `[a]` = `x7a`; `[s]` = fetched from source (a logged vocabulary gap). Source-link lines are the store's `q.line` + 1 (defect D1: the store is 0-based and does not say so).*
