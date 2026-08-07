# scripts.code_map.extract:run
function, scripts/code_map/extract.py:739, 48 lines

```python
def run(root, artifacts)
```

Extract the statement store for `root` into `artifacts`. Returns an exit code.

The prototype read its file list from a handwritten manifest and indexed
three hardcoded directories; both are now the discovered mappable corpus.

calls internal: Extractor, Extractor.run, mod_of, pass1
calls cross-module: scripts.code_map.discovery:discover_corpus
calls stdlib: builtins.len x6, builtins.open x3, builtins.print x3, os.path.join x3, builtins.str x2, ast.parse, builtins.list, json.dump, json.dumps, os.fspath, os.makedirs, sys.setrecursionlimit
reads internal: TABLES x4, REPORT_NAME, STATEMENTS_NAME
reads stdlib: os (module) x5, os.path x3, json (module) x2, ast (module), builtins.Exception, builtins.RecursionError, sys (module)
writes internal: run.artifacts
unresolved: 6 calls (dispatch-unknown-base)

referenced by: 1 sites in 1 modules (scripts.code_map.cli)
