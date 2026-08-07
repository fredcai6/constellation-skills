# scripts.code_map.extract:Extractor.attr_via_import
method, scripts/code_map/extract.py:356, 22 lines

```python
def attr_via_import(self, b, dotted, head, attr, depth)
```

`head` is bound by an import; resolve `head....attr` through it.

calls internal: chase x3, Extractor.class_member
calls stdlib: builtins.len
reads internal: UNRES x2
unresolved: 4 calls (dispatch-unknown-base)

referenced by: 2 sites, this module only
