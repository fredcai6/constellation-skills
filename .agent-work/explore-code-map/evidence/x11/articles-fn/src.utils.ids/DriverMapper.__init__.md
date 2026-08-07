[map index](../INDEX.md) / [`src.utils.ids`](INDEX.md) / [`DriverMapper`](DriverMapper.md)

# `DriverMapper.__init__`
*method* [s] · [`src/utils/ids.py:26`](C:/Programs/f1Brainz/src/utils/ids.py#L26) · 34 lines [s]

**Signature** [s]

```python
def __init__(self, override_file: Optional[str] = None)
```

> Initialize driver mapper
>
> Args:
>     override_file: Path to YAML file with manual override mappings

*(everything after the first line above is [s] — the store keeps only the summary line.)*

**Parameters**

- `override_file` — override_file: Path to YAML file with manual override mappings [a]

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `DriverMapper._load_manual_mappings` |
| writes | internal | `DriverMapper.driver_aliases`, `DriverMapper.manual_mappings`, `DriverMapper.override_file` |

*Not shown: 5 reads of its own parameters.*

**Referenced by**: no reference recorded inside the extraction window (9 `src/utils` files + 58 direct importers under `src/`; `scripts/` and `tests/` were not extracted).


---
*Generated from the statement store by `evidence/x11/render_fn.py`. Unmarked facts = `x7b` statements; `[a]` = `x7a`; `[s]` = fetched from source (a logged vocabulary gap). Source-link lines are the store's `q.line` + 1 (defect D1: the store is 0-based and does not say so).*
