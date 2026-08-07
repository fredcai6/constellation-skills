# scripts.code_map.extract:Extractor._func
method, scripts/code_map/extract.py:523, 40 lines

```python
def _func(self, node)
```

HOLE: no docstring

calls internal: Extractor.visit x5, Extractor.emit x3, Extractor.here x2, Extractor._prebind, Extractor.infer_annotation, Scope
calls stdlib: builtins.list x4, ast.get_docstring, builtins.len
reads internal: Extractor.clsstack x4, Extractor.encl x3, Extractor.scope x3, Extractor.mod x2
reads stdlib: ast (module)
writes internal: Extractor.scope x2
unresolved: 7 calls (dispatch-unknown-base), 28 reads (dispatch-unknown-base), 1 writes (dispatch-unknown-base)

referenced by: 2 sites, this module only
