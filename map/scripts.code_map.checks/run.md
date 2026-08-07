# scripts.code_map.checks:run
function, scripts/code_map/checks.py:198, 14 lines

```python
def run(root, artifacts, out)
```

Print every diagnostic. Always returns 0 -- these do not gate anything

until g1 rewrites them.

calls internal: function_local_imports, non_ascii_provenance, reconciliation, store_only_sites
calls cross-module: scripts.code_map.discovery:discover_corpus
calls stdlib: builtins.print x2, json.loads, os.path.isdir, pathlib.Path
reads cross-module: scripts.code_map.supplement:SUPPLEMENT_NAME
reads stdlib: json (module), os (module), os.path, pathlib (module)
writes internal: run.artifacts
unresolved: 1 calls (dispatch-unknown-base)

referenced by: 1 sites in 1 modules (scripts.code_map.cli)
