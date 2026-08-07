[map index](../INDEX.md) / [`src.utils.simplification_limits`](INDEX.md)

# `verify_simplification_limits`
*function* [s] · [`src/utils/simplification_limits.py:198`](C:/Programs/f1Brainz/src/utils/simplification_limits.py#L198) · 61 lines [s]

**Signature** [s]

```python
def verify_simplification_limits(*, roots: Sequence[str | Path] = DEFAULT_ROOTS, project_root: Path = PROJECT_ROOT, extra_paths: Optional[Sequence[str | Path]] = None, use_baseline: bool = False, baseline_path: Optional[Path] = None, metrics: Optional[Sequence[str]] = None) -> SimplificationLimitsResult
```

> Check simplification limits on Python under the given roots.
>
> Returns pass/fail and structured violations (path, symbol, metric, actual, limit).
> With use_baseline=True, paths listed in simplification_baseline.json are skipped.

*(everything after the first line above is [s] — the store keeps only the summary line.)*

**Parameters**

- `roots` — *[HOLE] undocumented parameter*
- `project_root` — *[HOLE] undocumented parameter*
- `extra_paths` — *[HOLE] undocumented parameter*
- `use_baseline` — *[HOLE] undocumented parameter*
- `baseline_path` — *[HOLE] undocumented parameter*
- `metrics` — *[HOLE] undocumented parameter*

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `load_baseline_config` x2, `SimplificationLimitsResult`, `_file_line_violations`, `_function_line_violations`, `_radon_complexity_violations`, `iter_python_files` |
| calls | stdlib | `builtins.frozenset` x4, `ast.parse`, `builtins.len`, `builtins.str` |
| reads | internal | `DEFAULT_BASELINE_PATH`, `Violation` |
| reads | stdlib | `typing.List` x2, `ast (module)`, `builtins.SyntaxError`, `pathlib.Path` |

*Not shown: 30 local-variable reads, 17 local-variable writes; 12 reads of its own parameters.*

**Unresolved by the extractor**: 8 calls (dispatch-unknown-base), 3 reads (dispatch-unknown-base), 3 reads (unbound-name)

**Referenced by**: 2 site(s) across 1 module(s) (all within this module)


---
*Generated from the statement store by `evidence/x11/render_fn.py`. Unmarked facts = `x7b` statements; `[a]` = `x7a`; `[s]` = fetched from source (a logged vocabulary gap). Source-link lines are the store's `q.line` + 1 (defect D1: the store is 0-based and does not say so).*
