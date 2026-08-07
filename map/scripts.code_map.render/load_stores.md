# scripts.code_map.render:load_stores
function, scripts/code_map/render.py:73, 70 lines

```python
def load_stores(artifacts)
```

Read the statement store and the supplement, and build every index the

page builders read. Safe to call repeatedly: it resets state first.

calls internal: intern x7, modof x5
calls stdlib: json.loads x2, builtins.open, builtins.sorted, pathlib.Path
reads internal: ent_supp x5, mod_supp x4, MODULES x3, alias x3, children x3, cont_at x3, BY_PKG x2, docs x2, edges x2, imported_by x2, imports_out x2, inbound x2, inherits x2, members_of x2, params x2
reads cross-module: scripts.code_map.extract:STATEMENTS_NAME, scripts.code_map.supplement:SUPPLEMENT_NAME
reads stdlib: json (module) x2, pathlib (module)
writes internal: alias[] x2, cont_at[], docs[], load_stores.artifacts
unresolved: 27 calls (dispatch-unknown-base), 1 reads (non-name-expr), 1 writes (non-name-expr)

referenced by: 1 sites, this module only
