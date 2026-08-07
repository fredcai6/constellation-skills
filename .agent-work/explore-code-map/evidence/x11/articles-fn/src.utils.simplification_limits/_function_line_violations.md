[map index](../INDEX.md) / [`src.utils.simplification_limits`](INDEX.md)

# `_function_line_violations`
*function* [s] · [`src/utils/simplification_limits.py:134`](C:/Programs/f1Brainz/src/utils/simplification_limits.py#L134) · 15 lines [s]

**Signature** [s]

```python
def _function_line_violations(path: Path, rel: str, tree: ast.AST) -> List[Violation]
```

> **[HOLE] no docstring** — this entity's purpose is not recorded in the source. Nothing in the store can supply it.

**Parameters**

- `path` — *[HOLE] undocumented parameter*
- `rel` — *[HOLE] undocumented parameter*
- `tree` — *[HOLE] undocumented parameter*

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `Violation`, `_function_spans` |
| reads | internal | `MAX_FUNCTION_LINES` x2, `Violation` |
| reads | stdlib | `typing.List` |

*Not shown: 7 local-variable reads, 5 local-variable writes; 2 reads of its own parameters.*

**Unresolved by the extractor**: 1 calls (dispatch-unknown-base)

**Referenced by**: 1 site(s) across 1 module(s) (all within this module)


---
*Generated from the statement store by `evidence/x11/render_fn.py`. Unmarked facts = `x7b` statements; `[a]` = `x7a`; `[s]` = fetched from source (a logged vocabulary gap). Source-link lines are the store's `q.line` + 1 (defect D1: the store is 0-based and does not say so).*
