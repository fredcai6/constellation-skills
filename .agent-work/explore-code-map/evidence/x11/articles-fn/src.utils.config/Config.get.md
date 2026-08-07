[map index](../INDEX.md) / [`src.utils.config`](INDEX.md) / [`Config`](Config.md)

# `Config.get`
*class method* [s] · [`src/utils/config.py:107`](C:/Programs/f1Brainz/src/utils/config.py#L107) · 14 lines [s]

**Signature** [s]

```python
def get(cls, key: str, default: Any = None) -> Any
```

> Get configuration value by key (supports nested keys with dot notation)

**Parameters**

- `key` — key (supports nested keys with dot notation) [a]
- `default` — *[HOLE] undocumented parameter*

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `Config.load_config` |
| reads | stdlib | `builtins.KeyError`, `builtins.TypeError` |

*Not shown: 5 local-variable reads, 5 local-variable writes; 3 reads of its own parameters.*

**Unresolved by the extractor**: 1 calls (dispatch-unknown-base)

**Referenced by**: 9 site(s) across 1 module(s) (all within this module)


---
*Generated from the statement store by `evidence/x11/render_fn.py`. Unmarked facts = `x7b` statements; `[a]` = `x7a`; `[s]` = fetched from source (a logged vocabulary gap). Source-link lines are the store's `q.line` + 1 (defect D1: the store is 0-based and does not say so).*
