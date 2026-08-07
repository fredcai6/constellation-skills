# src.utils.simplification_limits:_function_spans
function, src/utils/simplification_limits.py:105, 11 lines

```python
def _function_spans(tree: ast.AST) -> List[Tuple[str, int, int]]
```

HOLE: no docstring

calls stdlib: ast.walk x2, builtins.isinstance, builtins.max
reads stdlib: ast (module) x4, builtins.int x2, ast.AsyncFunctionDef, ast.FunctionDef, builtins.str, typing.List, typing.Tuple
unresolved: 1 calls (dispatch-unknown-base), 2 calls (dynamic), 3 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
