# scripts.map_orient:_gate
function, scripts/map_orient.py:1249, 13 lines

```python
def _gate(args: argparse.Namespace, code: int) -> int
```

The gate-vs-report dial, as a FLAG FLIP rather than a rebuild.

A ruling to gate or un-gate one of these checks should be an edit to the
command string in the template -- append `--report-only` -- not a change to
this module or to the checklist's shape. The verdict printed is identical
either way; only its blocking-ness moves.

calls stdlib: builtins.print, sys.stdout.flush
reads internal: EXIT_OK x2
reads stdlib: sys (module), sys.stdout
unresolved: 1 calls (dynamic)

referenced by: 5 sites, this module only
