# scripts.code_map.render:run
function, scripts/code_map/render.py:387, 53 lines

```python
def run(root, artifacts, out)
```

Render the page tree for `root` from `artifacts` into `out`. Returns an

exit code.

calls internal: load_stores, module_index, repo_name, summary_of, top_index
calls stdlib: builtins.len x4, builtins.open, builtins.print, builtins.sum, json.dump, json.dumps, os.fspath, os.makedirs, os.path.join, pathlib.Path, shutil.rmtree
reads internal: MODULES x2, ent_supp x2, REPORT_NAME, alias_missing, children
reads stdlib: os (module) x3, json (module) x2, os.path, pathlib (module), shutil (module)
writes internal: run.artifacts, run.out
unresolved: 8 calls (dispatch-unknown-base)

referenced by: 1 sites in 1 modules (scripts.code_map.cli)
