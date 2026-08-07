# scripts.code_map.extract:Extractor.class_member
method, scripts/code_map/extract.py:330, 25 lines

```python
def class_member(self, cls, attr, mod=None)
```

Look attr up on class cls, walking same-module bases. -> symbol|None

calls internal: Extractor.class_member
calls stdlib: builtins.set
reads internal: Extractor.mod, TABLES
writes internal: Extractor.class_member.mod
unresolved: 5 calls (dispatch-unknown-base), 8 reads (dispatch-unknown-base)

referenced by: 6 sites, this module only
