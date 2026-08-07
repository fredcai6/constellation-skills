# tests.test_worktree_precondition_wiring:EngineDeliberateBreakage
class, tests/test_worktree_precondition_wiring.py:113, 70 lines

```python
class EngineDeliberateBreakage(TestCase)
```

The wired precondition must actually block `start()` -- not just the

standalone coverage script -- when `--here` disagrees with the real
worktree, and must let `start()` proceed once it agrees. Runs against a
throwaway git repo built fresh in a temp dir, never this worktree's own
`.git` or the shared checkout.

- [setUp](EngineDeliberateBreakage.setUp.md) method: HOLE: no docstring
- [tearDown](EngineDeliberateBreakage.tearDown.md) method: HOLE: no docstring
- [_git](EngineDeliberateBreakage._git.md) method: HOLE: no docstring
- [_gated_checklist](EngineDeliberateBreakage._gated_checklist.md) method: HOLE: no docstring
- [test_start_refused_on_mismatch_then_succeeds_once_fixed](EngineDeliberateBreakage.test_start_refused_on_mismatch_then_succeeds_once_fixed.md) method: HOLE: no docstring

reads stdlib: builtins.dict, builtins.str

referenced by: none found
