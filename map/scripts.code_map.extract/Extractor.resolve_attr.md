# scripts.code_map.extract:Extractor.resolve_attr
method, scripts/code_map/extract.py:379, 63 lines

```python
def resolve_attr(self, node)
```

ast.Attribute -> (symbol, res, why)

calls internal: Extractor.class_member x4, Extractor.attr_via_import x2, _dotted
calls stdlib: builtins.isinstance x2, builtins.len
reads internal: Extractor.clsstack x6, UNRES x5, Extractor.table x4, Extractor.mod x3, Extractor.scope x2, BUILTINS
reads stdlib: ast (module) x2, ast.Name x2
unresolved: 3 calls (dispatch-unknown-base), 15 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
