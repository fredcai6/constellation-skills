# scripts.code_map.extract:Extractor.infer_type
method, scripts/code_map/extract.py:457, 10 lines

```python
def infer_type(self, value)
```

`v = Known(...)` / annotation -> (module, class) or None.

calls internal: Extractor.resolve_expr
calls stdlib: builtins.isinstance
reads internal: TABLES
reads stdlib: ast (module), ast.Call
unresolved: 2 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: 2 sites, this module only
