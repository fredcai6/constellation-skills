# scripts.code_map.extract:chase
function, scripts/code_map/extract.py:193, 27 lines

```python
def chase(mod, name, hops=0)
```

Follow a (module, name) through re-exports to its defining module.

Returns (symbol, res, why).

calls internal: chase x2
reads internal: TABLES x4, UNRES x3
unresolved: 2 calls (dispatch-unknown-base), 7 reads (dispatch-unknown-base)

referenced by: 10 sites, this module only
