# scripts.verify_worktree_isolation:main
function, scripts/verify_worktree_isolation.py:126, 49 lines

```python
def main(argv: list[str] | None = None) -> int
```

HOLE: no docstring

calls internal: check_distinct_real, check_here, current_toplevel, primary_checkout, registered_worktrees
calls stdlib: builtins.print x7, builtins.str x2, argparse.ArgumentParser, builtins.len, os.path.isdir
reads stdlib: sys (module) x5, sys.stderr x5, argparse (module) x2, builtins.RuntimeError x2, argparse.RawDescriptionHelpFormatter, builtins.__doc__, os (module), os.path
unresolved: 5 calls (dispatch-unknown-base), 8 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
