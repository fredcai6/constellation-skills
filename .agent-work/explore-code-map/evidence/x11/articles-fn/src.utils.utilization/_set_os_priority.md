[map index](../INDEX.md) / [`src.utils.utilization`](INDEX.md)

# `_set_os_priority`
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


---
*Generated from the statement store by `evidence/x11/render_fn.py`. Unmarked facts = `x7b` statements; `[a]` = `x7a`; `[s]` = fetched from source (a logged vocabulary gap). Source-link lines are the store's `q.line` + 1 (defect D1: the store is 0-based and does not say so).*
