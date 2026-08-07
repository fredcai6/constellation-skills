[map index](../INDEX.md) / [`src.utils.simplification_limits`](INDEX.md)

# `_function_spans`
*function* [s] · [`src/utils/simplification_limits.py:105`](C:/Programs/f1Brainz/src/utils/simplification_limits.py#L105) · 11 lines [s]

**Signature** [s]

```python
def _function_spans(tree: ast.AST) -> List[Tuple[str, int, int]]
```

> **[HOLE] no docstring** — this entity's purpose is not recorded in the source. Nothing in the store can supply it.

**Parameters**

- `tree` — *[HOLE] undocumented parameter*

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | stdlib | `ast.walk` x2, `builtins.isinstance`, `builtins.max` |
| reads | stdlib | `ast (module)` x4, `builtins.int` x2, `ast.AsyncFunctionDef`, `ast.FunctionDef`, `builtins.str`, `typing.List`, `typing.Tuple` |

*Not shown: 13 local-variable reads, 6 local-variable writes; 1 reads of its own parameters.*

**Unresolved by the extractor**: 1 calls (dispatch-unknown-base), 2 calls (dynamic), 3 reads (dispatch-unknown-base)

**Referenced by**: 1 site(s) across 1 module(s) (all within this module)


---
*Generated from the statement store by `evidence/x11/render_fn.py`. Unmarked facts = `x7b` statements; `[a]` = `x7a`; `[s]` = fetched from source (a logged vocabulary gap). Source-link lines are the store's `q.line` + 1 (defect D1: the store is 0-based and does not say so).*
