# scripts.map_orient:cmd_verify_frame
function, scripts/map_orient.py:1264, 37 lines

```python
def cmd_verify_frame(args: argparse.Namespace) -> int
```

HOLE: no docstring

calls internal: _gate x4, _read_text, _rel, frame_path, frame_verdict, map_inventory, receipt_path, receipt_problems, render_frame_report
calls stdlib: builtins.print x8, json.loads, pathlib.Path, sys.stdout.flush
reads internal: EXIT_RECEIPT_UNUSABLE x3, RECEIPT_MISSING x3, MODE_RESOLVED
reads stdlib: sys (module) x5, sys.stderr x4, builtins.OSError, builtins.ValueError, json (module), sys.stdout
unresolved: 8 calls (dispatch-unknown-base), 4 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
