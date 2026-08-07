# tests.test_episode_negative_control:_flag_pairs
function, tests/test_episode_negative_control.py:118, 21 lines

```python
def _flag_pairs(argv: tuple[str, ...]) -> list[tuple[str, str | None]]
```

`(flag, value)` for every flag in one issued argv, positionals dropped.

A value that itself begins with `--` would be mis-read as a flag; no engine verb
takes one, and the census is strictly *more* likely to fire in that case (an
unknown flag), never less — so the parse cannot turn a violation into a pass.

calls stdlib: builtins.len x2
reads internal: VALUELESS_FLAGS
reads stdlib: builtins.str x2, builtins.list, builtins.tuple
unresolved: 4 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
