[map index](../INDEX.md) / [`src.utils.utilization`](INDEX.md)

# `_detect_available_mem_gb`
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


---
*Generated from the statement store by `evidence/x11/render_fn.py`. Unmarked facts = `x7b` statements; `[a]` = `x7a`; `[s]` = fetched from source (a logged vocabulary gap). Source-link lines are the store's `q.line` + 1 (defect D1: the store is 0-based and does not say so).*
