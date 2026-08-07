# tests.test_worktree_precondition_wiring:EngineDeliberateBreakage._git
method, tests/test_worktree_precondition_wiring.py:136, 5 lines

```python
def _git(self, *args)
```

HOLE: no docstring

calls stdlib: builtins.str, subprocess.run
reads internal: EngineDeliberateBreakage.repo
reads stdlib: subprocess (module)

referenced by: 2 sites, this module only
