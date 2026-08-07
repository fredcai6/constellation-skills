[map index](../INDEX.md) / [`src.utils.simplification_limits`](INDEX.md)

# `iter_python_files`
*function* [s] · [`src/utils/simplification_limits.py:77`](C:/Programs/f1Brainz/src/utils/simplification_limits.py#L77) · 26 lines [s]

**Signature** [s]

```python
def iter_python_files(roots: Sequence[str | Path], *, project_root: Path = PROJECT_ROOT, extra_paths: Optional[Sequence[str | Path]] = None) -> List[Path]
```

> **[HOLE] no docstring** — this entity's purpose is not recorded in the source. Nothing in the store can supply it.

**Parameters**

- `roots` — *[HOLE] undocumented parameter*
- `project_root` — *[HOLE] undocumented parameter*
- `extra_paths` — *[HOLE] undocumented parameter*

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `_is_excluded_path` |
| calls | stdlib | `builtins.list` x2, `builtins.sorted` x2, `builtins.set`, `pathlib.Path` |
| reads | stdlib | `pathlib.Path` x2, `builtins.set`, `typing.List` |

*Not shown: 18 local-variable reads, 9 local-variable writes; 4 reads of its own parameters.*

**Unresolved by the extractor**: 7 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

**Referenced by**: 1 site(s) across 1 module(s) (all within this module)


---
*Generated from the statement store by `evidence/x11/render_fn.py`. Unmarked facts = `x7b` statements; `[a]` = `x7a`; `[s]` = fetched from source (a logged vocabulary gap). Source-link lines are the store's `q.line` + 1 (defect D1: the store is 0-based and does not say so).*
