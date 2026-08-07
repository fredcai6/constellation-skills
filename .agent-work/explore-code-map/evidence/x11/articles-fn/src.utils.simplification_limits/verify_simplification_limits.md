# src.utils.simplification_limits:verify_simplification_limits
function, src/utils/simplification_limits.py:198, 61 lines

```python
def verify_simplification_limits(*, roots: Sequence[str | Path] = DEFAULT_ROOTS, project_root: Path = PROJECT_ROOT, extra_paths: Optional[Sequence[str | Path]] = None, use_baseline: bool = False, baseline_path: Optional[Path] = None, metrics: Optional[Sequence[str]] = None) -> SimplificationLimitsResult
```

Check simplification limits on Python under the given roots.

Returns pass/fail and structured violations (path, symbol, metric, actual, limit).
With use_baseline=True, paths listed in simplification_baseline.json are skipped.

calls internal: load_baseline_config x2, SimplificationLimitsResult, _file_line_violations, _function_line_violations, _radon_complexity_violations, iter_python_files
calls stdlib: builtins.frozenset x4, ast.parse, builtins.len, builtins.str
reads internal: DEFAULT_BASELINE_PATH, Violation
reads stdlib: typing.List x2, ast (module), builtins.SyntaxError, pathlib.Path
unresolved: 8 calls (dispatch-unknown-base), 3 reads (dispatch-unknown-base), 3 reads (unbound-name)

referenced by: 2 sites, this module only
