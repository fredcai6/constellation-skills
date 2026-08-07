[map index](../INDEX.md) / [`src.utils.config`](INDEX.md) / [`Config`](Config.md)

# `Config._validate_config`
*class method* [s] · [`src/utils/config.py:243`](C:/Programs/f1Brainz/src/utils/config.py#L243) · 72 lines [s]

**Signature** [s]

```python
def _validate_config(cls)
```

> Validate configuration schema and required fields.
>
> Raises:
>     ConfigurationError: If required fields are missing or invalid

*(everything after the first line above is [s] — the store keeps only the summary line.)*

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | cross-module | `src.models.exceptions:ConfigurationError` x8 |
| calls | stdlib | `builtins.isinstance` x3, `builtins.list`, `builtins.type` |
| reads | internal | `Config._config_data` x2 |
| reads | stdlib | `builtins.int` x2, `builtins.list` x2, `builtins.dict` |

*Not shown: 37 local-variable reads, 12 local-variable writes; 2 reads of its own parameters.*

**Unresolved by the extractor**: 4 calls (dispatch-unknown-base), 3 reads (dispatch-unknown-base)

**Referenced by**: 1 site(s) across 1 module(s) (all within this module)


---
*Generated from the statement store by `evidence/x11/render_fn.py`. Unmarked facts = `x7b` statements; `[a]` = `x7a`; `[s]` = fetched from source (a logged vocabulary gap). Source-link lines are the store's `q.line` + 1 (defect D1: the store is 0-based and does not say so).*
