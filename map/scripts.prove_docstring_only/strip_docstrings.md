# scripts.prove_docstring_only:strip_docstrings
function, scripts/prove_docstring_only.py:67, 20 lines

```python
def strip_docstrings(tree: ast.AST) -> ast.AST
```

Drop the leading string-constant expression from every body that has one.

Bodies emptied by the strip get an explicit `Pass` so the tree stays valid;
`Pass` is inserted on both sides whenever it is inserted at all, so it can
never make two differing trees compare equal.

calls stdlib: builtins.isinstance x4, ast.Pass, ast.walk
reads stdlib: ast (module) x8, ast.AsyncFunctionDef, ast.ClassDef, ast.Constant, ast.Expr, ast.FunctionDef, ast.Module, builtins.str
unresolved: 4 reads (dispatch-unknown-base), 1 writes (dispatch-unknown-base)

referenced by: 2 sites, this module only
