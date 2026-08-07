# scripts.collect_feedback:_file_issues_cli
function, scripts/collect_feedback.py:621, 52 lines

```python
def _file_issues_cli(roots, new, open_unresolved, args, filer, commenter) -> int
```

Handle the --file-issues mode (file/comment); returns an exit code.

calls internal: merge_hits, sync_issues
calls stdlib: builtins.print x12, builtins.len x4
calls third-party: agent_work_root.durable_root
reads internal: INBOX_NAME
reads stdlib: sys (module) x3, sys.stderr x3, builtins.FileNotFoundError, subprocess (module), subprocess.CalledProcessError
unresolved: 3 calls (dispatch-unknown-base), 7 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
