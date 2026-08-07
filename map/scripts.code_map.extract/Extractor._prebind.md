# scripts.code_map.extract:Extractor._prebind
method, scripts/code_map/extract.py:567, 52 lines

```python
def _prebind(self, fnode)
```

HOLE: no docstring

calls internal: _target_names x6, Extractor.infer_annotation, Extractor.infer_type, pkg_of, resolve_rel
calls stdlib: builtins.isinstance x12, ast.walk, builtins.len
reads internal: Extractor.scope x12, Extractor.path
reads stdlib: ast (module) x18, ast.ImportFrom x3, ast.AnnAssign, ast.Assign, ast.AsyncFor, ast.AsyncFunctionDef, ast.AsyncWith, ast.ClassDef, ast.ExceptHandler, ast.For, ast.FunctionDef, ast.Global, ast.Import, ast.NamedExpr, ast.With, ast.comprehension
unresolved: 12 calls (dispatch-unknown-base), 30 reads (dispatch-unknown-base), 2 writes (dispatch-unknown-base)

referenced by: 1 sites, this module only
