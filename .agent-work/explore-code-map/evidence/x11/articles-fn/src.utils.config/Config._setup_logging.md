[map index](../INDEX.md) / [`src.utils.config`](INDEX.md) / [`Config`](Config.md)

# `Config._setup_logging`
*class method* [s] · [`src/utils/config.py:178`](C:/Programs/f1Brainz/src/utils/config.py#L178) · 23 lines [s]

**Signature** [s]

```python
def _setup_logging(cls)
```

> Setup logging configuration

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | stdlib | `logging.FileHandler`, `logging.StreamHandler`, `logging.basicConfig`, `logging.info`, `pathlib.Path` |
| reads | internal | `Config.LOGS_DIR` x2, `Config._config_data` |
| reads | stdlib | `logging (module)` x5 |

*Not shown: 7 local-variable reads, 5 local-variable writes; 3 reads of its own parameters.*

**Unresolved by the extractor**: 5 calls (dispatch-unknown-base), 1 calls (dynamic), 1 reads (dispatch-unknown-base)

**Referenced by**: 1 site(s) across 1 module(s) (all within this module)


---
*Generated from the statement store by `evidence/x11/render_fn.py`. Unmarked facts = `x7b` statements; `[a]` = `x7a`; `[s]` = fetched from source (a logged vocabulary gap). Source-link lines are the store's `q.line` + 1 (defect D1: the store is 0-based and does not say so).*
