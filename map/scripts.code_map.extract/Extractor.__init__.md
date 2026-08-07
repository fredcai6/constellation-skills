# scripts.code_map.extract:Extractor.__init__
method, scripts/code_map/extract.py:256, 15 lines

```python
def __init__(self, path, tree, core)
```

HOLE: no docstring

calls internal: Scope, mod_of
calls stdlib: os.path.relpath
reads internal: Extractor.mod x2, Extractor.scope x2, Extractor.table x2, ROOT, TABLES
reads stdlib: os (module), os.path
writes internal: Extractor.clsstack, Extractor.core, Extractor.encl, Extractor.mod, Extractor.out, Extractor.path, Extractor.rel, Extractor.scope, Extractor.table, Extractor.tree
unresolved: 3 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: none found
