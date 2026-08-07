[map index](../INDEX.md) / [`src.utils.constants`](INDEX.md)

# `get_weekend_sessions`
*function* [s] · [`src/utils/constants.py:336`](C:/Programs/f1Brainz/src/utils/constants.py#L336) · 16 lines [s]

**Signature** [s]

```python
def get_weekend_sessions(year: int, gp_name: str) -> List[str]
```

> Get session types for a specific Grand Prix weekend.
>
> Args:
>     year: Season year
>     gp_name: Grand Prix name
>
> Returns:
>     List of session types for that weekend

*(everything after the first line above is [s] — the store keeps only the summary line.)*

**Parameters**

- `year` — year: Season year [a]
- `gp_name` — gp_name: Grand Prix name [a]

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `is_sprint_weekend` |
| reads | internal | `LEGACY_SPRINT_WEEKEND_SESSIONS`, `LEGACY_SPRINT_YEARS`, `NORMAL_WEEKEND_SESSIONS`, `SPRINT_WEEKEND_SESSIONS` |

*Not shown: 3 reads of its own parameters.*

**Unresolved by the extractor**: 3 calls (dispatch-unknown-base)

**Referenced by**: 1 site(s) across 1 module(s) — src.data.collector


---
*Generated from the statement store by `evidence/x11/render_fn.py`. Unmarked facts = `x7b` statements; `[a]` = `x7a`; `[s]` = fetched from source (a logged vocabulary gap). Source-link lines are the store's `q.line` + 1 (defect D1: the store is 0-based and does not say so).*
