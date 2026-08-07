# scripts.file_issue_set:main
function, scripts/file_issue_set.py:316, 39 lines

```python
def main(argv: list[str] | None = None) -> int
```

HOLE: no docstring

calls internal: build_adapter, file_issue_set, wave_order
calls stdlib: builtins.print x5, pathlib.Path x4, builtins.len x3, argparse.ArgumentParser, builtins.str, json.loads
calls third-party: verify_issue_set.verify_issue_set
reads stdlib: sys (module) x3, sys.stderr x3, json (module) x2, argparse (module), builtins.OSError, builtins.RuntimeError, builtins.__doc__, json.JSONDecodeError
reads third-party: verify_issue_set.IssueSetError
unresolved: 10 calls (dispatch-unknown-base), 10 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
