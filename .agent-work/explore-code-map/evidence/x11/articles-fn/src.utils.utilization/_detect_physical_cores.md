[map index](../INDEX.md) / [`src.utils.utilization`](INDEX.md)

# `_detect_physical_cores`
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


---
*Generated from the statement store by `evidence/x11/render_fn.py`. Unmarked facts = `x7b` statements; `[a]` = `x7a`; `[s]` = fetched from source (a logged vocabulary gap). Source-link lines are the store's `q.line` + 1 (defect D1: the store is 0-based and does not say so).*
