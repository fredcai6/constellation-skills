[map index](../INDEX.md) / [`src.utils.constants`](INDEX.md)

# `is_sprint_weekend`
*function* [s] · [`src/utils/constants.py:281`](C:/Programs/f1Brainz/src/utils/constants.py#L281) · 12 lines [s]

**Signature** [s]

```python
def is_sprint_weekend(year: int, gp_name: str) -> bool
```

> Check if a Grand Prix has a sprint format.
>
> Args:
>     year: Season year
>     gp_name: Grand Prix name
>
> Returns:
>     True if sprint weekend, False otherwise

*(everything after the first line above is [s] — the store keeps only the summary line.)*

**Parameters**

- `year` — year: Season year [a]
- `gp_name` — gp_name: Grand Prix name [a]

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| reads | internal | `SPRINT_WEEKENDS` x2 |

*Not shown: 3 reads of its own parameters.*

**Referenced by**: 4 site(s) across 1 module(s) (all within this module)


---
*Generated from the statement store by `evidence/x11/render_fn.py`. Unmarked facts = `x7b` statements; `[a]` = `x7a`; `[s]` = fetched from source (a logged vocabulary gap). Source-link lines are the store's `q.line` + 1 (defect D1: the store is 0-based and does not say so).*
