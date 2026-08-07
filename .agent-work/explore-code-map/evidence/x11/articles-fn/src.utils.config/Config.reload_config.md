[map index](../INDEX.md) / [`src.utils.config`](INDEX.md) / [`Config`](Config.md)

# `Config.reload_config`
*class method* [s] · [`src/utils/config.py:317`](C:/Programs/f1Brainz/src/utils/config.py#L317) · 13 lines [s]

**Signature** [s]

```python
def reload_config(cls, config_file: str = 'default.yaml')
```

> Reload configuration from file.
>
> Args:
>     config_file: Name of config file to reload
>
> Returns:
>     Reloaded configuration dictionary

*(everything after the first line above is [s] — the store keeps only the summary line.)*

**Parameters**

- `config_file` — config_file: Name of config file to reload [a]

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `Config.load_config` |
| writes | internal | `Config._config_data`, `Config._config_source` |

*Not shown: 4 reads of its own parameters.*

**Referenced by**: no reference recorded inside the extraction window (9 `src/utils` files + 58 direct importers under `src/`; `scripts/` and `tests/` were not extracted).


---
*Generated from the statement store by `evidence/x11/render_fn.py`. Unmarked facts = `x7b` statements; `[a]` = `x7a`; `[s]` = fetched from source (a logged vocabulary gap). Source-link lines are the store's `q.line` + 1 (defect D1: the store is 0-based and does not say so).*
