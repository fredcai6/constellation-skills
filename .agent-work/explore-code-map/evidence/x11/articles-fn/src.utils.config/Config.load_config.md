[map index](../INDEX.md) / [`src.utils.config`](INDEX.md) / [`Config`](Config.md)

# `Config.load_config`
*class method* [s] · [`src/utils/config.py:49`](C:/Programs/f1Brainz/src/utils/config.py#L49) · 56 lines [s]

**Signature** [s]

```python
def load_config(cls, config_file: str = 'default.yaml') -> Dict[str, Any]
```

> Load and validate configuration from YAML file.
>
> Args:
>     config_file: Name of config file in configs/ directory
>
> Returns:
>     Validated configuration dictionary
>
> Raises:
>     ConfigurationError: If config file missing or invalid

*(everything after the first line above is [s] — the store keeps only the summary line.)*

**Parameters**

- `config_file` — config_file: Name of config file in configs/ directory [a]

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `Config._setup_fastf1_cache`, `Config._setup_logging`, `Config._validate_config` |
| calls | cross-module | `src.models.exceptions:ConfigurationError` x3 |
| calls | stdlib | `builtins.str` x4, `builtins.open`, `pathlib.Path` |
| calls | third-party | `yaml.safe_load` |
| reads | internal | `Config._config_data` x6, `Config._config_source` x2, `Config.CONFIG_DIR` |
| reads | third-party | `yaml (module)` x2, `yaml.YAMLError` |
| writes | internal | `Config._config_data`, `Config._config_source` |

*Not shown: 12 local-variable reads, 4 local-variable writes; 19 reads of its own parameters.*

**Unresolved by the extractor**: 2 calls (dispatch-unknown-base)

**Referenced by**: 3 site(s) across 1 module(s) (all within this module)


---
*Generated from the statement store by `evidence/x11/render_fn.py`. Unmarked facts = `x7b` statements; `[a]` = `x7a`; `[s]` = fetched from source (a logged vocabulary gap). Source-link lines are the store's `q.line` + 1 (defect D1: the store is 0-based and does not say so).*
