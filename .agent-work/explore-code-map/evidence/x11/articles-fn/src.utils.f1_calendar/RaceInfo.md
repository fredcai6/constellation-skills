[map index](../INDEX.md) / [`src.utils.f1_calendar`](INDEX.md)

# `RaceInfo`
*class* [s] · [`src/utils/f1_calendar.py:21`](C:/Programs/f1Brainz/src/utils/f1_calendar.py#L21) · 13 lines [s]

```python
class RaceInfo
```
**Decorators** [s]: `@dataclass`

> Information about an F1 race weekend.

**Fields**

| name | annotation [s] | value [s] | line | in store? |
| --- | --- | --- | --- | --- |
| `season` | `int` | — | 23 | name only |
| `race_number` | `int` | — | 24 | name only |
| `gp_name` | `str` | — | 25 | name only |
| `circuit_name` | `str` | — | 26 | name only |
| `country` | `str` | — | 27 | name only |
| `race_date` | `datetime` | — | 28 | name only |
| `quali_date` | `Optional[datetime]` | — | 29 | name only |
| `fp1_date` | `Optional[datetime]` | — | 30 | name only |
| `fp2_date` | `Optional[datetime]` | — | 31 | name only |
| `fp3_date` | `Optional[datetime]` | — | 32 | name only |
| `is_sprint_weekend` | `bool` | — | 33 | name only |

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| reads | stdlib | `datetime.datetime` x5, `typing.Optional` x4, `builtins.str` x3, `builtins.int` x2, `builtins.bool` |
| writes | internal | `RaceInfo.circuit_name`, `RaceInfo.country`, `RaceInfo.fp1_date`, `RaceInfo.fp2_date`, `RaceInfo.fp3_date`, `RaceInfo.gp_name`, `RaceInfo.is_sprint_weekend`, `RaceInfo.quali_date`, `RaceInfo.race_date`, `RaceInfo.race_number`, `RaceInfo.season` |

**Referenced by**: 15 site(s) across 1 module(s) (all within this module)


---
*Generated from the statement store by `evidence/x11/render_fn.py`. Unmarked facts = `x7b` statements; `[a]` = `x7a`; `[s]` = fetched from source (a logged vocabulary gap). Source-link lines are the store's `q.line` + 1 (defect D1: the store is 0-based and does not say so).*
