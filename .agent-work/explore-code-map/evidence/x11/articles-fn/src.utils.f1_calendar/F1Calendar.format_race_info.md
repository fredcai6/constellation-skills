[map index](../INDEX.md) / [`src.utils.f1_calendar`](INDEX.md) / [`F1Calendar`](F1Calendar.md)

# `F1Calendar.format_race_info`
*method* [s] · [`src/utils/f1_calendar.py:329`](C:/Programs/f1Brainz/src/utils/f1_calendar.py#L329) · 24 lines [s]

**Signature** [s]

```python
def format_race_info(self, race: RaceInfo) -> str
```

> Format race info for display.
>
> Args:
>     race: RaceInfo to format
>
> Returns:
>     Formatted string

*(everything after the first line above is [s] — the store keeps only the summary line.)*

**Parameters**

- `race` — race: RaceInfo to format [a]

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| reads | internal | `RaceInfo.quali_date` x2, `RaceInfo.race_date` x2, `RaceInfo.circuit_name`, `RaceInfo.country`, `RaceInfo.gp_name`, `RaceInfo.is_sprint_weekend`, `RaceInfo.race_number`, `RaceInfo.season` |
| reads | stdlib | `datetime.datetime.min`, `datetime.datetime` |

*Not shown: 7 local-variable reads, 1 local-variable writes; 10 reads of its own parameters.*

**Unresolved by the extractor**: 2 calls (chained-attribute), 7 calls (dispatch-unknown-base)

**Referenced by**: no reference recorded inside the extraction window (9 `src/utils` files + 58 direct importers under `src/`; `scripts/` and `tests/` were not extracted).


---
*Generated from the statement store by `evidence/x11/render_fn.py`. Unmarked facts = `x7b` statements; `[a]` = `x7a`; `[s]` = fetched from source (a logged vocabulary gap). Source-link lines are the store's `q.line` + 1 (defect D1: the store is 0-based and does not say so).*
