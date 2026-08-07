[map index](../INDEX.md) / [`src.utils.config`](INDEX.md)

# `get_config_value`
*function* [s] · [`src/utils/config.py:367`](C:/Programs/f1Brainz/src/utils/config.py#L367) · 15 lines [s]

**Signature** [s]

```python
def get_config_value(key: str, default: Any = None) -> Any
```

> Get configuration value by key.
>
> Args:
>     key: Configuration key (supports dot notation for nested keys)
>     default: Default value if key not found
>
> Returns:
>     Configuration value or default

*(everything after the first line above is [s] — the store keeps only the summary line.)*

**Parameters**

- `key` — key: Configuration key (supports dot notation for nested keys) [a]
- `default` — default: Default value if key not found [a]

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `Config.get` |
| reads | internal | `Config` |
| reads | stdlib | `builtins.Exception` |

*Not shown: 3 reads of its own parameters.*

**Referenced by**: 1 site(s) across 1 module(s) — src.physics.physics_config


---
*Generated from the statement store by `evidence/x11/render_fn.py`. Unmarked facts = `x7b` statements; `[a]` = `x7a`; `[s]` = fetched from source (a logged vocabulary gap). Source-link lines are the store's `q.line` + 1 (defect D1: the store is 0-based and does not say so).*
