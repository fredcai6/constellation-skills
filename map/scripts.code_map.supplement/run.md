# scripts.code_map.supplement:run
function, scripts/code_map/supplement.py:121, 86 lines

```python
def run(root, artifacts)
```

Write the supplement for `root` into `artifacts`. Returns an exit code.

calls internal: attrs_of, doc_split, mod_of
calls cross-module: scripts.code_map.discovery:discover_corpus
calls stdlib: builtins.len x7, builtins.open x3, os.path.join x3, builtins.isinstance x2, builtins.print x2, builtins.str x2, json.dump x2, os.fspath x2, ast.literal_eval, ast.parse, os.makedirs, sys.setrecursionlimit
reads internal: GAPS, REPORT_NAME, SUPPLEMENT_NAME
reads stdlib: os (module) x6, ast (module) x4, os.path x3, builtins.Exception x2, json (module) x2, ast.Assign, ast.Name, sys (module)
writes internal: run.artifacts
unresolved: 4 calls (dispatch-unknown-base), 4 reads (dispatch-unknown-base), 1 writes (non-name-expr)

referenced by: 1 sites in 1 modules (scripts.code_map.cli)
