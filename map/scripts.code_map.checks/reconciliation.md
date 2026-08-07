# scripts.code_map.checks:reconciliation
function, scripts/code_map/checks.py:85, 43 lines

```python
def reconciliation(root, supp, artifacts)
```

(c) statements `contains` vs the supplement's AST walk.

Reconcile on SOURCE POSITION, not symbol: the store's symbols are not
unique (D2 flattens nested names), so a symbol-keyed dict silently loses
sites.

calls internal: _statements
calls stdlib: builtins.print x10, builtins.len x7, builtins.set x6, builtins.sorted x2, ast.iter_child_nodes, ast.parse, ast.walk, builtins.dict, builtins.isinstance, builtins.type, collections.Counter, pathlib.Path
reads stdlib: ast (module) x6, ast.AsyncFunctionDef, ast.ClassDef, ast.FunctionDef, builtins.Exception, collections (module), pathlib (module)
writes internal: reconciliation.root
unresolved: 4 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base), 1 reads (non-name-expr)

referenced by: 1 sites, this module only
