[map index](../INDEX.md) / [`src.utils.config`](INDEX.md)

# `load_config`
*function* [s] · [`src/utils/config.py:338`](C:/Programs/f1Brainz/src/utils/config.py#L338) · 27 lines [s]

**Signature** [s]

```python
def load_config(config_file: str = 'default.yaml') -> Dict[str, Any]
```

> Load configuration from YAML file.
>
> Args:
>     config_file: Path to config file or name of file in configs/ directory
>
> Returns:
>     Configuration dictionary

*(everything after the first line above is [s] — the store keeps only the summary line.)*

**Parameters**

- `config_file` — config_file: Path to config file or name of file in configs/ directory [a]

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `Config.load_config` |
| calls | stdlib | `builtins.open`, `pathlib.Path` |
| calls | third-party | `yaml.safe_load` |
| reads | internal | `Config` x2, `Config.CONFIG_DIR` |
| reads | stdlib | `builtins.Exception` |
| reads | third-party | `yaml (module)` x2, `yaml.YAMLError` |

*Not shown: 3 local-variable reads, 2 local-variable writes; 3 reads of its own parameters.*

**Unresolved by the extractor**: 2 calls (dispatch-unknown-base)

**Referenced by**: no reference recorded inside the extraction window (9 `src/utils` files + 58 direct importers under `src/`; `scripts/` and `tests/` were not extracted).


---
*Generated from the statement store by `evidence/x11/render_fn.py`. Unmarked facts = `x7b` statements; `[a]` = `x7a`; `[s]` = fetched from source (a logged vocabulary gap). Source-link lines are the store's `q.line` + 1 (defect D1: the store is 0-based and does not say so).*
