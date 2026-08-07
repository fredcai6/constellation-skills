[map index](../INDEX.md) / [`src.utils.simplification_limits`](INDEX.md)

# `SimplificationLimitsResult`
*class* [s] · [`src/utils/simplification_limits.py:48`](C:/Programs/f1Brainz/src/utils/simplification_limits.py#L48) · 11 lines [s]

```python
class SimplificationLimitsResult
```
**Decorators** [s]: `@dataclass`

> **[HOLE] no docstring** — this entity's purpose is not recorded in the source. Nothing in the store can supply it.

**Fields**

| name | annotation [s] | value [s] | line | in store? |
| --- | --- | --- | --- | --- |
| `passed` | `bool` | — | 49 | name only |
| `violations` | `List[Violation]` | — | 50 | name only |
| `files_checked` | `int` | — | 51 | name only |

**Members**

- [`SimplificationLimitsResult.to_dict`](SimplificationLimitsResult.to_dict.md) — *method* — **[HOLE] undocumented**

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| reads | internal | `Violation` |
| reads | stdlib | `builtins.bool`, `builtins.dict`, `builtins.int`, `typing.List` |
| writes | internal | `SimplificationLimitsResult.files_checked`, `SimplificationLimitsResult.passed`, `SimplificationLimitsResult.violations` |

**Referenced by**: 3 site(s) across 1 module(s) (all within this module)


---
*Generated from the statement store by `evidence/x11/render_fn.py`. Unmarked facts = `x7b` statements; `[a]` = `x7a`; `[s]` = fetched from source (a logged vocabulary gap). Source-link lines are the store's `q.line` + 1 (defect D1: the store is 0-based and does not say so).*
