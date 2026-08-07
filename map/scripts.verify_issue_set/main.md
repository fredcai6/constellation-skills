# scripts.verify_issue_set:main
function, scripts/verify_issue_set.py:139, 25 lines

```python
def main(argv: list[str] | None = None) -> int
```

HOLE: no docstring

calls internal: verify_issue_set
calls stdlib: builtins.print x4, pathlib.Path x2, argparse.ArgumentParser, builtins.len, json.loads
reads internal: IssueSetError
reads stdlib: sys (module) x3, sys.stderr x3, builtins.OSError x2, json (module) x2, argparse (module), builtins.__doc__, json.JSONDecodeError
unresolved: 5 calls (dispatch-unknown-base), 3 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
