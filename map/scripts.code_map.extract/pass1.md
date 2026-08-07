# scripts.code_map.extract:pass1
function, scripts/code_map/extract.py:180, 6 lines

```python
def pass1(root, files)
```

Index the module-level binding table of every file in the corpus.

calls internal: build_table
calls stdlib: os.path.join
reads internal: TABLES
reads stdlib: os (module), os.path
writes internal: TABLES[]
unresolved: 1 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
