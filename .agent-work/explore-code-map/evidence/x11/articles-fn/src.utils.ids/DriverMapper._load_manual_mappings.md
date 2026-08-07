[map index](../INDEX.md) / [`src.utils.ids`](INDEX.md) / [`DriverMapper`](DriverMapper.md)

# `DriverMapper._load_manual_mappings`
*method* [s] · [`src/utils/ids.py:61`](C:/Programs/f1Brainz/src/utils/ids.py#L61) · 15 lines [s]

**Signature** [s]

```python
def _load_manual_mappings(self) -> Dict[str, Dict[str, str]]
```

> Load manual override mappings from YAML file

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | stdlib | `builtins.isinstance`, `builtins.len`, `builtins.open` |
| calls | third-party | `yaml.safe_load` |
| reads | internal | `DriverMapper.override_file` x2, `logger` x2 |
| reads | stdlib | `builtins.Exception`, `builtins.dict` |
| reads | third-party | `yaml (module)` |

*Not shown: 6 local-variable reads, 2 local-variable writes; 2 reads of its own parameters.*

**Unresolved by the extractor**: 2 calls (dispatch-unknown-base)

**Referenced by**: 1 site(s) across 1 module(s) (all within this module)


---
*Generated from the statement store by `evidence/x11/render_fn.py`. Unmarked facts = `x7b` statements; `[a]` = `x7a`; `[s]` = fetched from source (a logged vocabulary gap). Source-link lines are the store's `q.line` + 1 (defect D1: the store is 0-based and does not say so).*
