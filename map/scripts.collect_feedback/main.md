# scripts.collect_feedback:main
function, scripts/collect_feedback.py:675, 67 lines

```python
def main(argv: list[str] | None = None, *, filer=gh_file_issue, commenter=gh_comment_issue) -> int
```

HOLE: no docstring

calls internal: collect x2, _file_issues_cli, mark_collected, render_report
calls stdlib: builtins.print x5, argparse.ArgumentParser, builtins.list, json.loads, pathlib.Path
reads stdlib: pathlib.Path x4, json (module) x2, sys (module) x2, sys.stderr x2, argparse (module), builtins.OSError, builtins.__doc__, json.JSONDecodeError
unresolved: 14 calls (dispatch-unknown-base), 9 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
