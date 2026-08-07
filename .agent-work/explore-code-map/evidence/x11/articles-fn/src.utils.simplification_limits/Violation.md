[map index](../INDEX.md) / [`src.utils.simplification_limits`](INDEX.md)

# `Violation`
*class* [s] · [`src/utils/simplification_limits.py:32`](C:/Programs/f1Brainz/src/utils/simplification_limits.py#L32) · 13 lines [s]

```python
class Violation
```
**Decorators** [s]: `@dataclass(frozen=True)`

> **[HOLE] no docstring** — this entity's purpose is not recorded in the source. Nothing in the store can supply it.

**Fields**

| name | annotation [s] | value [s] | line | in store? |
| --- | --- | --- | --- | --- |
| `path` | `str` | — | 33 | name only |
| `symbol` | `Optional[str]` | — | 34 | name only |
| `metric` | `str` | — | 35 | name only |
| `actual` | `int` | — | 36 | name only |
| `limit` | `int` | — | 37 | name only |

**Members**

- [`Violation.format_message`](Violation.format_message.md) — *method* — **[HOLE] undocumented**

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| reads | stdlib | `builtins.str` x4, `builtins.int` x2, `typing.Optional` |
| writes | internal | `Violation.actual`, `Violation.limit`, `Violation.metric`, `Violation.path`, `Violation.symbol` |

**Referenced by**: 10 site(s) across 1 module(s) (all within this module)


---
*Generated from the statement store by `evidence/x11/render_fn.py`. Unmarked facts = `x7b` statements; `[a]` = `x7a`; `[s]` = fetched from source (a logged vocabulary gap). Source-link lines are the store's `q.line` + 1 (defect D1: the store is 0-based and does not say so).*
