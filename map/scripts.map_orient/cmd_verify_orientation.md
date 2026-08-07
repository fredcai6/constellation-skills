# scripts.map_orient:cmd_verify_orientation
function, scripts/map_orient.py:1221, 26 lines

```python
def cmd_verify_orientation(args: argparse.Namespace) -> int
```

HOLE: no docstring

calls internal: _gate, _rel, receipt_path, render_verify_report, verify_verdict
calls stdlib: builtins.print x6, builtins.isinstance x2, json.loads, pathlib.Path, sys.stdout.flush
reads internal: EXIT_RECEIPT_UNUSABLE x2, RECEIPT_MISSING x2
reads stdlib: sys (module) x4, sys.stderr x3, builtins.OSError, builtins.ValueError, builtins.dict, builtins.list, builtins.object, json (module), sys.stdout
unresolved: 7 calls (dispatch-unknown-base), 3 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
