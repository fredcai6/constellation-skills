# src.utils.simplification_limits:_radon_complexity_violations
function, src/utils/simplification_limits.py:151, 29 lines

```python
def _radon_complexity_violations(paths: List[Path], project_root: Path) -> List[Violation]
```

HOLE: no docstring

calls internal: Violation
calls stdlib: builtins.RuntimeError, builtins.str
reads internal: MAX_CYCLOMATIC_COMPLEXITY x2, Violation
reads stdlib: builtins.ImportError, builtins.SyntaxError, typing.List
unresolved: 4 calls (dispatch-unknown-base), 3 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
