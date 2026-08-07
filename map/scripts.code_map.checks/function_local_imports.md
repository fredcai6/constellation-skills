# scripts.code_map.checks:function_local_imports
function, scripts/code_map/checks.py:152, 44 lines

```python
def function_local_imports(root, artifacts, files)
```

Defect D4: names bound by a function-scoped import, and how many

local-resolved calls/reads are one of them.

calls internal: _statements
calls stdlib: builtins.print x6, builtins.sum x3, ast.walk x2, builtins.isinstance x2, builtins.len x2, ast.parse, builtins.dict, builtins.round, collections.Counter, collections.defaultdict, pathlib.Path
reads stdlib: ast (module) x7, collections (module) x2, ast.AsyncFunctionDef, ast.FunctionDef, ast.Import, ast.ImportFrom, builtins.Exception, builtins.set, pathlib (module)
writes internal: function_local_imports.root
unresolved: 11 calls (dispatch-unknown-base), 4 reads (dispatch-unknown-base), 1 reads (non-name-expr)

referenced by: 1 sites, this module only
