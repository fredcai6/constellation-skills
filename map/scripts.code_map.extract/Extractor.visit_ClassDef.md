# scripts.code_map.extract:Extractor.visit_ClassDef
method, scripts/code_map/extract.py:499, 23 lines

```python
def visit_ClassDef(self, node)
```

HOLE: no docstring

calls internal: Extractor.emit x3, Extractor.visit x2, Extractor.here, Extractor.pos_of, Extractor.resolve_expr, Scope
calls stdlib: ast.get_docstring
reads internal: Extractor.clsstack x4, Extractor.encl x2, Extractor.mod x2, Extractor.scope
reads stdlib: ast (module)
writes internal: Extractor.scope x2
unresolved: 6 calls (dispatch-unknown-base), 11 reads (dispatch-unknown-base)

referenced by: none found
