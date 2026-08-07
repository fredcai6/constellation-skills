# scripts.code_map.extract:Extractor.run
method, scripts/code_map/extract.py:490, 8 lines

```python
def run(self)
```

HOLE: no docstring

calls internal: Extractor.emit, Extractor.visit
calls stdlib: ast.get_docstring
reads internal: Extractor.tree x2, Extractor.mod, Extractor.out
reads stdlib: ast (module)
unresolved: 2 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
