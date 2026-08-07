# scripts.agent_work_root:_git_rev_parse
function, scripts/agent_work_root.py:58, 16 lines

```python
def _git_rev_parse(base: str, arg: str) -> str
```

Read-only `git -C base rev-parse <arg>`, run with cwd=base so relative

outputs resolve against `base`. Raises RuntimeError on non-zero exit, and
lets OSError (git absent / bad cwd) propagate — both caught by the caller.

calls stdlib: builtins.RuntimeError, subprocess.run
reads stdlib: subprocess (module)
unresolved: 2 calls (dispatch-unknown-base), 3 reads (dispatch-unknown-base)

referenced by: 2 sites, this module only
