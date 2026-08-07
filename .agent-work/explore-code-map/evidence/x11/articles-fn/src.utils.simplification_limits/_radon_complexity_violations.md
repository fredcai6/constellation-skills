[map index](../INDEX.md) / [`src.utils.simplification_limits`](INDEX.md)

# `_radon_complexity_violations`
*function* [s] · [`src/utils/simplification_limits.py:151`](C:/Programs/f1Brainz/src/utils/simplification_limits.py#L151) · 29 lines [s]

**Signature** [s]

```python
def _radon_complexity_violations(paths: List[Path], project_root: Path) -> List[Violation]
```

> **[HOLE] no docstring** — this entity's purpose is not recorded in the source. Nothing in the store can supply it.

**Parameters**

- `paths` — *[HOLE] undocumented parameter*
- `project_root` — *[HOLE] undocumented parameter*

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `Violation` |
| calls | stdlib | `builtins.RuntimeError`, `builtins.str` |
| reads | internal | `MAX_CYCLOMATIC_COMPLEXITY` x2, `Violation` |
| reads | stdlib | `builtins.ImportError`, `builtins.SyntaxError`, `typing.List` |

*Not shown: 1 local-variable calls, 11 local-variable reads, 6 local-variable writes; 2 reads of its own parameters.*

**Unresolved by the extractor**: 4 calls (dispatch-unknown-base), 3 reads (dispatch-unknown-base)

**Referenced by**: 1 site(s) across 1 module(s) (all within this module)


---
*Generated from the statement store by `evidence/x11/render_fn.py`. Unmarked facts = `x7b` statements; `[a]` = `x7a`; `[s]` = fetched from source (a logged vocabulary gap). Source-link lines are the store's `q.line` + 1 (defect D1: the store is 0-based and does not say so).*
