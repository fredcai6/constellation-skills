# scripts.map_orient:cmd_orient
function, scripts/map_orient.py:1180, 39 lines

```python
def cmd_orient(args: argparse.Namespace) -> int
```

HOLE: no docstring

calls internal: _now_iso, _rel, build_orientation, build_receipt, collect_candidates, degraded_record_is_complete, exit_code_for, missing_degraded_fields, pin_substitutes, probe_fallbacks, probe_root, receipt_path, render_orient_report, write_receipt
calls stdlib: builtins.print x4, pathlib.Path, sys.stdout.flush
reads internal: EXIT_DEGRADED_UNDISCHARGED, EXIT_UNRESOLVABLE_ROOT
reads stdlib: sys (module) x4, sys.stderr x3, sys.stdout
unresolved: 6 calls (dispatch-unknown-base), 10 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
