[map index](../INDEX.md) / [`src.utils.config`](INDEX.md) / [`Config`](Config.md)

# `Config.db_path_for_year`
*class method* [s] · [`src/utils/config.py:36`](C:/Programs/f1Brainz/src/utils/config.py#L36) · 3 lines [s]

**Signature** [s]

```python
def db_path_for_year(cls, year: int) -> Path
```

> Return the per-season SQLite path: data/f1_data_{year}.db

**Parameters**

- `year` — *[HOLE] undocumented parameter*

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| reads | internal | `Config.PROJECT_ROOT` |

*Not shown: 2 reads of its own parameters.*

**Referenced by**: no reference recorded inside the extraction window (9 `src/utils` files + 58 direct importers under `src/`; `scripts/` and `tests/` were not extracted).


---
*Generated from the statement store by `evidence/x11/render_fn.py`. Unmarked facts = `x7b` statements; `[a]` = `x7a`; `[s]` = fetched from source (a logged vocabulary gap). Source-link lines are the store's `q.line` + 1 (defect D1: the store is 0-based and does not say so).*
