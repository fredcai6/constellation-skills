# scripts.code_map.extract:Extractor.resolve_name
method, scripts/code_map/extract.py:289, 34 lines

```python
def resolve_name(self, node)
```

ast.Name -> (symbol, res, why)

calls internal: chase x2, Extractor.from_binding
reads internal: Extractor.table x6, Extractor.clsstack x3, Extractor.mod x2, Extractor.scope x2, TABLES x2, UNRES x2, BUILTINS
unresolved: 4 calls (dispatch-unknown-base), 16 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
