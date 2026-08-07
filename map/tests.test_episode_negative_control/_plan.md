# tests.test_episode_negative_control:_plan
function, tests/test_episode_negative_control.py:363, 54 lines

```python
def _plan(work_id: str, ok_flag: Path, child: str | None) -> dict
```

Two gates, identical on parent and child so the LEASE is the only difference.

`g2.c2` is a `command` check whose entire signal is its exit code — `test -f` on an
absolute path. #315: the engine passes no `cwd` on the command branch and discards
the check's stdout, so a check that printed its verdict would print into a void and
a relative path would resolve against an uncontrolled directory. An exit-code
vocabulary is the only thing that reaches the spine, so the induced failure is built
as one: flag absent -> exit 1, flag present -> exit 0.

- [gate](_plan.gate.md) method: HOLE: no docstring

reads stdlib: builtins.str x2, builtins.dict
unresolved: 1 calls (dispatch-unknown-base)

referenced by: 3 sites, this module only
