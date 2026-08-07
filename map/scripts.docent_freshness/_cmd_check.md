# scripts.docent_freshness:_cmd_check
function, scripts/docent_freshness.py:135, 30 lines

```python
def _cmd_check(args: argparse.Namespace) -> int
```

HOLE: no docstring

calls internal: _resolve_site_html, compute_stamp, read_embedded_stamp
calls stdlib: builtins.print x5, pathlib.Path x2
reads stdlib: sys (module) x3, sys.stderr x3
unresolved: 2 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
